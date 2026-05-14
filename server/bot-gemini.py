#
# Copyright (c) 2024–2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""simple-chatbot - Pipecat Voice Agent

This module implements a chatbot using Google's Gemini Live model for natural language
processing. It includes:
- Real-time audio/video interaction through Daily
- Animated robot avatar

The bot runs as part of a pipeline that processes audio/video frames and manages
the conversation flow.

Required AI services:
- Gemini Live (LLM)

Run the bot using::

    uv run bot.py
"""

import os
from curriculum import LESSONS
from lesson_state import LessonState

from dotenv import load_dotenv
from loguru import logger
from PIL import Image
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import (
    BotStartedSpeakingFrame,
    BotStoppedSpeakingFrame,
    Frame,
    LLMRunFrame,
    OutputImageRawFrame,
    SpriteFrame,
)
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.runner.types import DailyRunnerArguments, RunnerArguments, SmallWebRTCRunnerArguments
from pipecat.services.google.gemini_live.llm import GeminiLiveLLMService
from pipecat.transports.base_transport import BaseTransport, TransportParams
from pipecat.transports.daily.transport import DailyParams, DailyTransport
from pipecat.transports.smallwebrtc.connection import SmallWebRTCConnection
from pipecat.transports.smallwebrtc.transport import SmallWebRTCTransport

load_dotenv(override=True)

sprites = []
script_dir = os.path.dirname(__file__)

# Load sequential animation frames
for i in range(1, 26):
    # Build the full path to the image file
    full_path = os.path.join(script_dir, f"assets/robot0{i}.png")
    # Get the filename without the extension to use as the dictionary key
    # Open the image and convert it to bytes
    with Image.open(full_path) as img:
        sprites.append(OutputImageRawFrame(image=img.tobytes(), size=img.size, format=img.format))

# Create a smooth animation by adding reversed frames
flipped = sprites[::-1]
sprites.extend(flipped)

# Define static and animated states
quiet_frame = sprites[0]  # Static frame for when bot is listening
talking_frame = SpriteFrame(images=sprites)  # Animation sequence for when bot is talking


class TalkingAnimation(FrameProcessor):
    """Manages the bot's visual animation states.

    Switches between static (listening) and animated (talking) states based on
    the bot's current speaking status.
    """

    def __init__(self):
        super().__init__()
        self._is_talking = False

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        """Process incoming frames and update animation state.

        Args:
            frame: The incoming frame to process
            direction: The direction of frame flow in the pipeline
        """
        await super().process_frame(frame, direction)

        # Switch to talking animation when bot starts speaking
        if isinstance(frame, BotStartedSpeakingFrame):
            if not self._is_talking:
                await self.push_frame(talking_frame)
                self._is_talking = True
        # Return to static frame when bot stops speaking
        elif isinstance(frame, BotStoppedSpeakingFrame):
            await self.push_frame(quiet_frame)
            self._is_talking = False

        await self.push_frame(frame, direction)


async def run_bot(transport: BaseTransport):
    """Main bot execution function.

    Sets up and runs the bot pipeline including:
    - Gemini Live model integration
    - Voice activity detection
    - Animation processing
    - RTVI event handling
    """
    lesson_state = LessonState()
    lesson_state.start_lesson("greetings")
    current_lesson = LESSONS[lesson_state.current_lesson]
    lesson_context = f"""
Current lesson: {lesson_state.current_lesson}

Objective:
{current_lesson['objective']}

Vocabulary:
{current_lesson['vocabulary']}

Practice Questions:
{current_lesson['practice_questions']}
"""

    print("CURRENT LESSON:")
    print(LESSONS[lesson_state.current_lesson])

    # Initialize the Gemini Live model
    llm = GeminiLiveLLMService(
        api_key=os.getenv("GOOGLE_API_KEY"),
        settings=GeminiLiveLLMService.Settings(
            system_instruction="""
You are Linguo, a real-time voice-first AI language tutor.

Your job is to teach beginner Spanish to English speakers through short interactive spoken conversations.

IMPORTANT RULES:
- Keep responses extremely short and conversational.
- Never speak more than 2 short sentences at once.
- Ask the learner to respond frequently.
- Pause often for interaction.
- Speak naturally like a friendly human tutor.
- Avoid long explanations.
- Avoid special characters because responses are spoken aloud.

TEACHING STYLE:
Every lesson should follow this structure:
1. Introduce the learning objective briefly.
2. Give one simple example.
3. Ask the learner to repeat or answer.
4. Give corrective feedback.
5. Check understanding before moving on.

MODES:
You support:
- Teaching mode
- Quiz mode
- Conversation practice
- Doubt resolution

INTERRUPTIONS:
If the learner interrupts with a doubt or question:
- answer briefly in English
- then smoothly resume the lesson

QUIZ BEHAVIOR:
- Ask one question at a time
- Wait for learner response
- Give encouraging but specific feedback
- Accept semantically correct answers

CONVERSATION PRACTICE:
- Roleplay realistic situations
- Correct mistakes gently
- Encourage the learner to speak more

PRONUNCIATION FEEDBACK:
When the learner makes pronunciation mistakes:
- provide short actionable corrections
- model the correct pronunciation

IMPORTANT:
The learner should speak more than you.
You are a tutor, not a lecturer.
""",
            voice="Charon",  # Aoede, Charon, Fenrir, Kore, Puck
        ),
    )

    messages = [
    {
        "role": "user",
        "content": f"""
The learner wants to learn beginner Spanish through voice interaction.

{lesson_context}

Start teaching the lesson step-by-step.
Keep responses short and interactive.
Ask the learner questions frequently.
"""
    }
    ]

    # Set up conversation context and management
    # The context_aggregator will automatically collect conversation context
    context = LLMContext(messages)
    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(
            vad_analyzer=SileroVADAnalyzer(),
        ),
    )

    ta = TalkingAnimation()

    # Pipeline - assembled from reusable components
    pipeline = Pipeline(
        [
            transport.input(),
            user_aggregator,
            llm,
            ta,
            transport.output(),
            assistant_aggregator,
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
    )

    # Queue initial static frame so video starts immediately
    await task.queue_frame(quiet_frame)

    @task.rtvi.event_handler("on_client_ready")
    async def on_client_ready(rtvi):
        # Kick off the conversation
        await task.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info("Client connected")

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info("Client disconnected")
        await task.cancel()

    runner = PipelineRunner(handle_sigint=False)

    await runner.run(task)


async def bot(runner_args: RunnerArguments):
    """Main bot entry point."""

    transport = None

    match runner_args:
        case DailyRunnerArguments():
            transport = DailyTransport(
                runner_args.room_url,
                runner_args.token,
                "Pipecat Bot",
                params=DailyParams(
                    audio_in_enabled=True,
                    audio_out_enabled=True,
                    video_out_enabled=True,
                    video_out_width=1024,
                    video_out_height=576,
                ),
            )
        case SmallWebRTCRunnerArguments():
            webrtc_connection: SmallWebRTCConnection = runner_args.webrtc_connection

            transport = SmallWebRTCTransport(
                webrtc_connection=webrtc_connection,
                params=TransportParams(
                    audio_in_enabled=True,
                    audio_out_enabled=True,
                    video_out_enabled=True,
                    video_out_width=1024,
                    video_out_height=576,
                ),
            )
        case _:
            logger.error(f"Unsupported runner arguments type: {type(runner_args)}")
            return

    await run_bot(transport)


if __name__ == "__main__":
    from pipecat.runner.run import main

    main()
