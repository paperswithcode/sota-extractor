import io
import json
import gzip
from sota_extractor import errors
from sota_extractor.consts import Format
from sota_extractor.taskdb import TaskDB


def dumps(tdb: TaskDB) -> str:
    """Render sota data to a json string."""
    return json.dumps(tdb.export(), indent=2, sort_keys=True)


def dump(tdb: TaskDB, output: str, fmt=Format.json, encoding="utf-8"):
    """Write sota data to file.

    Intention of this helper function is to always have maximally similar
    json files after export. To do that it will always sort json object keys
    alphabetically, use the same indent, same encoding and same serializer.

    Args:
        tdb (TaskDB): Populated TaskDB instance.
        output (str): Path to the output file in which the data should be
            serialized.
        fmt (Format): Serialization format.
        encoding (str): File encoding.
    """
    if fmt == Format.json:
        with io.open(output, mode="w", encoding=encoding) as fp:
            fp.write(dumps(tdb))
    elif fmt == Format.json_gz:
        with gzip.open(output, mode="wb") as fp:
            fp.write(dumps(tdb).encode(encoding))
    else:
        raise errors.UnsupportedFormat(fmt)


def load(filename, fmt=Format.json, encoding="utf-8"):
    """Load sota data from file.

    Args:
        filename (str): Path to the file from which the data should be
            deserialized.
        fmt (Format): Serialization format.
        encoding (str): File encoding.
    """
    if fmt == Format.json:
        with io.open(filename, mode="r", encoding=encoding) as fp:
            return json.load(fp)
    elif fmt == Format.json_gz:
        with gzip.open(filename, mode="rb") as fp:
            return json.loads(fp.read().decode(encoding))
    else:
        raise errors.UnsupportedFormat(fmt)
