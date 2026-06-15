from typing import List, Dict
import uuid


def _split_paragraphs(text:str) -> List[str]:
    """Split on blank lines into paragraph."""

    paras = []
    buf = []
    for line in text.splitlines():
        if line.strip():
            buf.append(line)
        else:
            if buf:
                paras.append("".join(buf).strip())
                buf = []
        if buf:
            paras.append("".join(buf).strip())
    return paras

def chunk_text(
        text: str,
        source: str,
        max_chars: int = 800,
        overlap_chars: int = 120,
    ) -> List[Dict]:

        """
        Custom chunker:
        - splits into paragraphs
        - builds sliding window chunks with overlap
        - keeps chunks under max_chars
        """

        paragraphs = _split_paragraphs(text)
        if not paragraphs:
            return[]

        chunks: List[Dict] = []

        #Build chunks with sliding window over paragraphs
        current = ""
        for para in paragraphs:
            if not current:
                current = para
                continue

            #if adding this paragraph exceeds max_chars. flush current chunk
            if len(current) + 1 + len(para) > max_chars:
                chunks.append(current)
                # start new chunk with some overlap from previous tail +new para                
                if overlap_chars > 0 and len(current) > overlap_chars:
                    overlap = current[-overlap_chars:]
                    current = (overlap + " " + para).strip()
                else:
                    current = para
            else:
                current = (current + " " + para).strip()
        if current:
            chunks.append(current)

        # Wrap in metadata
        return [
            {
                "id": str(uuid.uuid4()),
                "text": c,
                "meta": {
                    "source": source,
                    "chunk_index": i,
               },
            }
            for i, c in enumerate(chunks)
        ]

