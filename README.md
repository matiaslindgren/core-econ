# core-econ

* Unofficial visualizations for The Core Team's [The Economy](https://core-econ.org/the-economy/).
* Written mostly in Python, using [pandas](https://pandas.pydata.org/docs/) for data transformations and [Altair](https://altair-viz.github.io/) for visualizations.
* Fully static: HTML, JavaScript, CSS only.

## Building

1. Install [`make`](https://www.gnu.org/software/make/)
2. Install Python dependencies
    ```bash
    python3.9 -m pip install --user -r requirements.txt
    ```
3. Build content into `./out`
    ```bash
    make --jobs all
    ```
4. Serve content locally
    ```bash
    python3 -m http.server --directory ./out
    ```
    then go to [localhost:8000](http://localhost:8000).
5. If 4. does not work, open `./out/index.html` in a web browser.
