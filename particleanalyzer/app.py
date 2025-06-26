from particleanalyzer.core.ui import create_interface
from particleanalyzer.core.languages import i18n


def main(port=8000, api_key=""):
    demo = create_interface(api_key)
    demo.queue(default_concurrency_limit=5, api_open=False).launch(
        server_name="127.0.0.1",
        server_port=port,
        pwa=True,
        favicon_path="particleanalyzer/assets/icon/search-solid.png",
        i18n=i18n,
    )
