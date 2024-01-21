import multiprocessing
from multiprocessing import Process, Pipe, Queue
import pyaudio

# Voice2Text 
from AltoGPT.speech2text_module.run_recorder import run_recorder

# QA Model 
from AltoGPT.qa_module.generate_answer import generate_answer

# Video Generator
from AltoGPT.video_module.run_video import run_video


if __name__ == "__main__":

    listening_parent, listening_child = Pipe()
    qa_parent, qa_child = Pipe()
    answer_parent, answer_child = Pipe()
    voice2text_queue = Queue()

    voice2text_process = Process(target=run_recorder, args=(listening_parent, answer_parent, voice2text_queue))
    qa_process = Process(target=generate_answer, args=(voice2text_queue, qa_parent))

    voice2text_process.start()
    qa_process.start()

    print("Starting the application...")
    run_video(listening_child, qa_child, answer_child)

    voice2text_process.join()
    qa_process.join()

    print("Application has been terminated.")
