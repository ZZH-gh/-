"""Gzip compress all compiled JSON knowledge packs (PKG-02)."""
import gzip
import os

src = "prompt_tool/knowledge_packs_compiled"
for f in os.listdir(src):
    if f.endswith(".json") and not f.endswith(".gz"):
        json_path = os.path.join(src, f)
        gz_path = json_path + ".gz"
        with open(json_path, "rb") as sf, gzip.open(gz_path, "wb") as df:
            df.write(sf.read())
        print("OK - Compressed:", f)
print("Knowledge packs compressed")
