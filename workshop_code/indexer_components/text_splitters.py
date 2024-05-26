import re
from typing import List

class SimpleCharacterTextSplitter:
  def __init__(self, chunk_size: int, overlap_size: int):
    self.chunk_size = chunk_size
    self.overlap_size = overlap_size
    
  def split_text(self, text: str) -> List[str]:
    raise NotImplementedError("Implement this method and delete this exception.")