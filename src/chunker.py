import re
import hashlib
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class EvidenceChunk:
    """
    Represents a semantically coherent chunk of research evidence.
    Maintains provenance to document_id, research_session_id, and section context.
    """
    chunk_id: str
    document_id: str
    research_session_id: str
    content: str
    section_heading: str = ""
    char_start: int = 0
    char_end: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "research_session_id": self.research_session_id,
            "content": self.content,
            "section_heading": self.section_heading,
            "char_start": self.char_start,
            "char_end": self.char_end,
            "metadata": self.metadata,
        }


HEADING_PATTERN = re.compile(r"^(#{1,6}\s+.+|[A-Z0-9\s]{4,}:)$", re.MULTILINE)
TABLE_LINE_PATTERN = re.compile(r"^\s*\|.*\|\s*$")


def _is_table_block(lines: List[str]) -> bool:
    """Checks if a sequence of lines forms a markdown table."""
    if len(lines) < 2:
        return False
    return all(TABLE_LINE_PATTERN.match(l) for l in lines if l.strip())


def chunk_document_semantically(
    text: str,
    document_id: str = "",
    research_session_id: str = "",
    max_chars: int = 1200,
    overlap_chars: int = 150,
    extra_metadata: Optional[Dict[str, Any]] = None,
) -> List[EvidenceChunk]:
    """
    Splits document text into EvidenceChunks respecting:
    1. Markdown headings and section context
    2. Markdown tables (kept intact without row fragmentation)
    3. Paragraph boundaries and natural sentence breaks
    """
    if not text or not text.strip():
        return []

    doc_id = document_id or f"doc_{hashlib.md5(text[:100].encode('utf-8')).hexdigest()[:8]}"
    extra_meta = extra_metadata or {}

    # Split text into structural blocks (headings, tables, paragraphs)
    raw_lines = text.splitlines()
    blocks = []  # List of tuples: (block_type, heading_context, content, char_start, char_end)

    current_heading = "Overview"
    current_block_lines = []
    in_table = False
    current_pos = 0

    for line in raw_lines:
        stripped = line.strip()
        is_heading = bool(HEADING_PATTERN.match(stripped))
        is_table_line = bool(TABLE_LINE_PATTERN.match(stripped))

        if is_heading:
            if current_block_lines:
                block_content = "\n".join(current_block_lines).strip()
                if block_content:
                    blocks.append(("table" if in_table else "text", current_heading, block_content))
                current_block_lines = []
                in_table = False

            # Update heading context
            current_heading = re.sub(r"^#+\s*", "", stripped)
            blocks.append(("heading", current_heading, stripped))
            continue

        if is_table_line:
            if not in_table:
                # Flush existing text block before starting table
                if current_block_lines:
                    block_content = "\n".join(current_block_lines).strip()
                    if block_content:
                        blocks.append(("text", current_heading, block_content))
                    current_block_lines = []
                in_table = True
            current_block_lines.append(line)
        else:
            if in_table:
                # Table ended
                if current_block_lines:
                    block_content = "\n".join(current_block_lines).strip()
                    if block_content:
                        blocks.append(("table", current_heading, block_content))
                    current_block_lines = []
                in_table = False

            if stripped == "":
                if current_block_lines:
                    block_content = "\n".join(current_block_lines).strip()
                    if block_content:
                        blocks.append(("text", current_heading, block_content))
                    current_block_lines = []
            else:
                current_block_lines.append(line)

    if current_block_lines:
        block_content = "\n".join(current_block_lines).strip()
        if block_content:
            blocks.append(("table" if in_table else "text", current_heading, block_content))

    # Assemble blocks into coherent chunks <= max_chars
    chunks: List[EvidenceChunk] = []
    current_chunk_parts: List[str] = []
    current_chunk_len = 0
    active_heading = "Overview"
    chunk_index = 0
    char_offset = 0

    def flush_chunk():
        nonlocal current_chunk_parts, current_chunk_len, chunk_index, char_offset
        if not current_chunk_parts:
            return

        chunk_text_body = "\n\n".join(current_chunk_parts).strip()
        if not chunk_text_body:
            current_chunk_parts = []
            current_chunk_len = 0
            return

        chk_id = f"{doc_id}_chk_{chunk_index:03d}"
        c_start = char_offset
        c_end = char_offset + len(chunk_text_body)
        char_offset = c_end

        meta = dict(extra_meta)
        meta["section_heading"] = active_heading
        meta["chunk_index"] = chunk_index

        chunks.append(
            EvidenceChunk(
                chunk_id=chk_id,
                document_id=doc_id,
                research_session_id=research_session_id,
                content=chunk_text_body,
                section_heading=active_heading,
                char_start=c_start,
                char_end=c_end,
                metadata=meta,
            )
        )
        chunk_index += 1

        # Prepare overlap from the last element if it's text
        if overlap_chars > 0 and len(current_chunk_parts) > 1:
            last_part = current_chunk_parts[-1]
            if len(last_part) <= overlap_chars:
                current_chunk_parts = [last_part]
                current_chunk_len = len(last_part)
            else:
                overlap_text = last_part[-overlap_chars:]
                current_chunk_parts = [overlap_text]
                current_chunk_len = len(overlap_text)
        else:
            current_chunk_parts = []
            current_chunk_len = 0

    for b_type, b_heading, b_content in blocks:
        if b_type == "heading":
            if current_chunk_parts:
                flush_chunk()
            active_heading = b_heading
            continue

        b_len = len(b_content)

        # If a single table or paragraph exceeds max_chars
        if b_len > max_chars:
            flush_chunk()
            active_heading = b_heading
            # For tables, preserve table headers across segments if possible
            if b_type == "table":
                t_lines = b_content.splitlines()
                header = t_lines[:2] if len(t_lines) >= 2 else []
                sub_rows = t_lines[2:] if len(t_lines) >= 2 else t_lines
                cur_t_lines = list(header)
                cur_t_len = sum(len(l) for l in cur_t_lines)

                for row in sub_rows:
                    if cur_t_len + len(row) + 1 > max_chars and len(cur_t_lines) > len(header):
                        current_chunk_parts = ["\n".join(cur_t_lines)]
                        flush_chunk()
                        cur_t_lines = list(header)
                        cur_t_len = sum(len(l) for l in cur_t_lines)
                    cur_t_lines.append(row)
                    cur_t_len += len(row) + 1

                if cur_t_lines:
                    current_chunk_parts = ["\n".join(cur_t_lines)]
                    flush_chunk()
            else:
                # Long text paragraph - sentence split
                sentences = re.split(r"(?<=[.!?])\s+", b_content)
                for s in sentences:
                    if current_chunk_len + len(s) + 1 > max_chars and current_chunk_parts:
                        flush_chunk()
                    current_chunk_parts.append(s)
                    current_chunk_len += len(s) + 1
            continue

        if current_chunk_len + b_len + 2 > max_chars and current_chunk_parts:
            flush_chunk()

        active_heading = b_heading
        current_chunk_parts.append(b_content)
        current_chunk_len += b_len + 2

    flush_chunk()

    # Fallback if text was purely unformatted
    if not chunks and text.strip():
        chunks.append(
            EvidenceChunk(
                chunk_id=f"{doc_id}_chk_000",
                document_id=doc_id,
                research_session_id=research_session_id,
                content=text.strip(),
                section_heading="Overview",
                char_start=0,
                char_end=len(text.strip()),
                metadata=dict(extra_meta),
            )
        )

    return chunks


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 100) -> List[str]:
    """
    Backward-compatible text chunker returning List[str].
    Uses semantic chunking internally to prevent mid-sentence or mid-table fractures.
    """
    if not text:
        return []

    # If semantic chunking produces structured chunks, return their contents
    semantic_chunks = chunk_document_semantically(
        text,
        max_chars=chunk_size,
        overlap_chars=overlap,
    )
    if semantic_chunks:
        return [c.content for c in semantic_chunks]

    # Fallback sliding window
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap

    return chunks




