from pathlib import Path

import unasync

async_dir = Path(__file__).parent.parent / "patent_client" / "_async"
async_files = list(str(p) for p in async_dir.glob("**/*.py"))

print(len(async_files))

unasync.unasync_files(
    async_files,
    rules=[
        unasync.Rule(
            "patent_client/_async/",
            "patent_client/_sync/",
            additional_replacements={
                "AsyncClient": "Client",
                "pytest.mark.anyio": "",
            },
        )
    ],
)
