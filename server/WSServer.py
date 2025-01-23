import asyncio
import signal
import websockets

from voice_changer.VoiceChangerParamsManager import VoiceChangerParamsManager
from voice_changer.utils.VoiceChangerParams import VoiceChangerParams
from voice_changer.VoiceChangerManager import VoiceChangerManager

import argparse
from distutils.util import strtobool


def setupArgParser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--logLevel", type=str, default="error", help="Log level info|critical|error. (default: error)")
    parser.add_argument("-p", type=int, default=18888, help="port")
    parser.add_argument("--https", type=strtobool, default=False, help="use https")
    parser.add_argument("--test_connect", type=str, default="8.8.8.8", help="test connect to detect ip in https mode. default 8.8.8.8")
    parser.add_argument("--httpsKey", type=str, default="ssl.key", help="path for the key of https")
    parser.add_argument("--httpsCert", type=str, default="ssl.cert", help="path for the cert of https")
    parser.add_argument("--httpsSelfSigned", type=strtobool, default=True, help="generate self-signed certificate")

    parser.add_argument("--model_dir", type=str, default="model_dir", help="path to model files")
    parser.add_argument("--sample_mode", type=str, default="production", help="rvc_sample_mode")

    parser.add_argument("--content_vec_500", type=str, default="pretrain/checkpoint_best_legacy_500.pt", help="path to content_vec_500 model(pytorch)")
    parser.add_argument("--content_vec_500_onnx", type=str, default="pretrain/content_vec_500.onnx", help="path to content_vec_500 model(onnx)")
    parser.add_argument("--content_vec_500_onnx_on", type=strtobool, default=True, help="use or not onnx for  content_vec_500")
    parser.add_argument("--hubert_base", type=str, default="pretrain/hubert_base.pt", help="path to hubert_base model(pytorch)")
    parser.add_argument("--hubert_base_jp", type=str, default="pretrain/rinna_hubert_base_jp.pt", help="path to hubert_base_jp model(pytorch)")
    parser.add_argument("--hubert_soft", type=str, default="pretrain/hubert/hubert-soft-0d54a1f4.pt", help="path to hubert_soft model(pytorch)")
    parser.add_argument("--whisper_tiny", type=str, default="pretrain/whisper_tiny.pt", help="path to hubert_soft model(pytorch)")
    parser.add_argument("--nsf_hifigan", type=str, default="pretrain/nsf_hifigan/model", help="path to nsf_hifigan model(pytorch)")
    parser.add_argument("--crepe_onnx_full", type=str, default="pretrain/crepe_onnx_full.onnx", help="path to crepe_onnx_full")
    parser.add_argument("--crepe_onnx_tiny", type=str, default="pretrain/crepe_onnx_tiny.onnx", help="path to crepe_onnx_tiny")
    parser.add_argument("--rmvpe", type=str, default="pretrain/rmvpe.pt", help="path to rmvpe")
    parser.add_argument("--rmvpe_onnx", type=str, default="pretrain/rmvpe.onnx", help="path to rmvpe onnx")

    parser.add_argument("--host", type=str, default='127.0.0.1', help="IP address of the network interface to listen for HTTP connections. Specify 0.0.0.0 to listen on all interfaces.")
    parser.add_argument("--allowed-origins", action='append', default=[], help="List of URLs to allow connection from, i.e. https://example.com. Allows http(s)://127.0.0.1:{port} and http(s)://localhost:{port} by default.")

    return parser


parser = setupArgParser()
args, unknown = parser.parse_known_args()

voiceChangerParams = VoiceChangerParams(
    model_dir=args.model_dir,
    content_vec_500=args.content_vec_500,
    content_vec_500_onnx=args.content_vec_500_onnx,
    content_vec_500_onnx_on=args.content_vec_500_onnx_on,
    hubert_base=args.hubert_base,
    hubert_base_jp=args.hubert_base_jp,
    hubert_soft=args.hubert_soft,
    nsf_hifigan=args.nsf_hifigan,
    crepe_onnx_full=args.crepe_onnx_full,
    crepe_onnx_tiny=args.crepe_onnx_tiny,
    rmvpe=args.rmvpe,
    rmvpe_onnx=args.rmvpe_onnx,
    sample_mode=args.sample_mode,
    whisper_tiny=args.whisper_tiny,
)

async def handler(websocket, path):
    """
    This function will handle incoming WebSocket connections.

    :param websocket: The WebSocket connection object.
    :param path: The URI path that was requested by the client.
    """
    print(f"Client connected: {path}")

    try:
        async for message in websocket:
            print(f"Received message from client: {message}")
            voiceChangerManager.update_settings("tran", message)
            response = f"Echo: {message}"
            await websocket.send(response)
    except websockets.exceptions.ConnectionClosedOK:
        print("Client disconnected")
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Connection closed with error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

async def main():
    """
    The main function to start the WebSocket server.
    """
    stop_event = asyncio.Event()
    # Signal handler to stop the server
    def on_signal(signal, frame):
        print("Received exit signal, shutting down...")
        stop_event.set()

    # Register signal handlers for SIGINT and SIGTERM
    signal.signal(signal.SIGINT, on_signal)
    signal.signal(signal.SIGTERM, on_signal)

    
    # Start the server
    async with websockets.serve(handler, "localhost", 8765):
        print("WebSocket server started on ws://localhost:8765")
        await stop_event.wait()  # Wait until a stop event is set

if __name__ == "__main__":
    voiceChangerManager = VoiceChangerManager.get_instance(voiceChangerParams)
    asyncio.run(main())