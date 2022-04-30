# core-econ

Interactive economics visualizations based on [The Economy](https://core-econ.org/the-economy/) using
* Python
* [pandas](https://pandas.pydata.org/docs/)
* [Jinja](https://jinja.palletsprojects.com/en/3.1.x/)
* [Altair](https://altair-viz.github.io/)
* [Vega-Lite](https://vega.github.io/vega-lite/)

## Running locally

### Requirements

- [`make`](https://www.gnu.org/software/make/)
- [`python3.9`](https://docs.python.org/3.9/)
- Download all datasets in CSV format into `./data`.
See the value of key `url` in all `./metadata/*.yaml` files for URLs of data sources.

### Short version

```bash
make -j run
```

### Long version

1. Install Python dependencies (if virtualenv is preferred, create and activate it first)
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
