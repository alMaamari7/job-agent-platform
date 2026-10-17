from pathlib import Path
from uuid import uuid4
from urllib.parse import urlparse
from fastapi import UploadFile
import json
from app.schemas.candidate_source import CandidateSource
from app.enums.candidate_source import SourceType


UPLOAD_DIR = Path("uploads/candidate_sources")


class CandidateSourceService:

    async def save_file(
        self,
        file: UploadFile,
    ) -> CandidateSource:

        UPLOAD_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )
        source_id = uuid4()

        suffix = Path(file.filename or "").suffix

        stored_filename = f"{source_id}{suffix}"

        file_path = UPLOAD_DIR / stored_filename

        content = await file.read()
        

        with open(file_path, "wb") as destination:
            destination.write(content)

        source = CandidateSource(
            source_id=source_id,
            source_type=SourceType.FILE,
            original_filename=file.filename,
            file_path=str(file_path),
        )

        self.register_source(source)

        return source


    def _detect_url_source_type(
        self,
        url: str,
    ) -> SourceType:

        parsed_url = urlparse(url)

        hostname = parsed_url.hostname or ""

        hostname = hostname.lower()

        if hostname == "github.com" or hostname.endswith(".github.com"):
            return SourceType.GITHUB

        return SourceType.URL




    def save_url(
            self,
            url: str,
        ) -> CandidateSource:

            source_type = self._detect_url_source_type(url)

            source = CandidateSource(
                source_id=uuid4(),
                source_type=source_type,
                original_filename=None,
                file_path=None,
                source_url=url,
            )

            self.register_source(source)
            return source
    



    def register_source(
        self,
        source: CandidateSource,
    ) -> None:

        registry_path = UPLOAD_DIR / "sources.json"

        data = {
            "sources": []
        }

        if registry_path.exists():

            try:
                with open(
                    registry_path,
                    "r",
                    encoding="utf-8",
                ) as file:

                    content = file.read().strip()

                    if content:
                        data = json.loads(content)

            except json.JSONDecodeError:
                raise ValueError(
                    f"Candidate source registry contains invalid JSON: "
                    f"{registry_path}"
                )

        data.setdefault(
            "sources",
            [],
        )

        data["sources"].append(
            source.model_dump(
                mode="json"
            )
        )

        with open(
            registry_path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
            )

    def get_sources(
        self,
    ) -> list[CandidateSource]:

        registry_path = UPLOAD_DIR / "sources.json"

        if not registry_path.exists():
            return []

        with open(
            registry_path,
            "r",
            encoding="utf-8",
        ) as file:

            content = file.read().strip()

        if not content:
            return []

        try:
            data = json.loads(content)

        except json.JSONDecodeError as error:
            raise ValueError(
                f"Candidate source registry contains invalid JSON: "
                f"{registry_path}"
            ) from error

        return [
            CandidateSource.model_validate(source)
            for source in data.get(
                "sources",
                []
            )
        ]