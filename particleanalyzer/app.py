import os
from particleanalyzer.core.ui import create_interface
from particleanalyzer.core.languages import i18n


def assets_path(name: str):
    return os.path.join(os.path.dirname(__file__), "assets", name)


def main(port=8000, api_key=""):
    demo = create_interface(api_key)
    demo.queue(default_concurrency_limit=5, api_open=False).launch(
        server_name="127.0.0.1",
        server_port=port,
        pwa=True,
        favicon_path=f'{assets_path("")}/icon/search-solid.png',
        i18n=i18n,
        ssr_mode=True,
        show_api=False,
        inbrowser=True,
        allowed_paths=[assets_path("")],
    )
