# core-econ

* Visualizing [The Economy](https://core-econ.org/the-economy/).
* Written mostly in Python, using [pandas](https://pandas.pydata.org/docs/) for data transformations and [Altair](https://altair-viz.github.io/) for visualizations.
* Fully static: HTML, JavaScript, CSS only.

## Running locally

### Requirements

- [`make`](https://www.gnu.org/software/make/)
- [`python3.9`](https://docs.python.org/3.9/)

### Short version

```bash
make run
```

### Long version

1. Install Python dependencies (if virtualenv is preferred, use it here)
    ```bash
    python3.9 -m pip install --user -r requirements.txt
    ```
2. Build content into `./out`
    ```bash
    make --jobs all
    ```
3. Serve content locally
    ```bash
    python3.9 -m http.server --directory ./out
    ```
    then go to [localhost:8000](http://localhost:8000).
4. If 3. does not work, open `./out/index.html` in a web browser.
