# {fas}`download` Installation
Installation instructions:

::::{tab-set}
:::{tab-item} Pip
Install the latest stable version from [PyPI](https://pypi.org/project/patent_client/):
```
pip install patent_client
```
:::
:::{tab-item} Pre-release
If you would like to use the latest development (pre-release) version:
```
pip install --pre patent_client
```
:::
:::{tab-item} Local development
See {ref}`contributing` for setup steps for local development
:::
::::

If you are only interested in using the USPTO API’s, no further setup is necessary. Skip ahead to the next section.

If you want to take advantage of the European Patent Office’s Open Patent Services, which supports Inpadoc and Epo Register documents, you will need to set up your API key. You can do this in one of two ways:

System Wide Configuration (Recommended)
---------------------------------------

**Step 1:** Go to [EPO Open Patent Services](https://www.epo.org/searching-for-patents/data/web-services/ops.html) and
register a new account (Free up to 4GB of data / month, which is usually more than sufficient).

**Step 2:** Log in to EPO OPS, and click on "My Apps," add a new app, and write down the corresponding API *Consumer Key* and *Consumer Key Secret*.

**Step 3:** Import patent_client from anywhere. E.g.

```bash

    $ python
    Python 3.6.5 (default, Jul 12 2018, 11:37:09)
    >>> import patent_client
```

This will set up an empty settings file, located at **~/.iprc**. The IPRC file is a JSON object containing settings for the project.

**Step 4:** Edit the IPRC file to contain your user key and secret. E.g.

```json

    {
        "EpoOpenPatentServices": {
            "ApiKey": "<Consumer Key Here>",
            "Secret": "<Consumer Key Secret Here>"
        }
    }
```

**Step 5:** PROFIT! Every time you import a model that requires EPO OPS access, you will automatically be logged on using that key and secret.

Environment Variables (Less Recommended)
----------------------------------------

Alternatively, you can set the environment variables as:

```bash

    EPO_KEY="<Consumer Key Here>"
    EPO_SECRET="<Consumer Key Secret Here>"
```