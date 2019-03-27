import io
import json
import enum
import gzip
from sota_extractor import errors


class Format(enum.Enum):
    """Output format.

    At the moment only supported format is JSON, but in the future YAML support
    is planned.
    """

    json = "json"
    json_gz = "json.gz"


def dump(data, filename, fmt=Format.json, encoding="utf-8"):
    """Write sota data to file.

    Intention of this helper function is to always have maximally similar
    json files after export. To do that it will always sort json object keys
    alphabetically, use the same indent, same encoding and same serializer.

    Args:
        data: Data for serialization.
        filename (str): Path to the file in which the data should be
            serialized.
        fmt (Format): Serialization format.
        encoding (str): File encoding.
    """
    if fmt == Format.json:
        with io.open(filename, mode="w", encoding=encoding) as fp:
            json.dump(data, fp=fp, indent=2, sort_keys=True)
    elif fmt == Format.json_gz:
        with gzip.open(filename, mode="wb") as fp:
            fp.write(
                json.dumps(data, fp=fp, indent=2, sort_keys=True).encode(
                    encoding
                )
            )
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
