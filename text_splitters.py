import re
from typing import List

class SimpleCharacterTextSplitter:
  def __init__(self, chunk_size: int, overlap_size: int):
    self.chunk_size = chunk_size
    self.overlap_size = overlap_size
    
  def split_text(self, text: str) -> List[str]:
    text_wo_multi_whitespace = re.sub(r"\s+", " ", text)  # Remove multiple whitespaces
    text_words = re.split(r"\s", text_wo_multi_whitespace)  # Split text by single whitespace

    chunks = []
    for i in range(0, len(text_words), self.chunk_size):  # Iterate through & chunk data
        chunk = " ".join(text_words[max(i - self.overlap_size, 0): i + self.chunk_size])  # Join a set of words into a string
        chunks.append(chunk)
    return chunks