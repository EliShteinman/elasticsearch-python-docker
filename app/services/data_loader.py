import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class NewsDataLoader:
    """Load real news data from 20newsgroups dataset"""

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and process text content"""
        if not text:
            return ""

        # Remove email headers and quoted text
        lines = text.split('\n')
        cleaned_lines = []
        skip_quoted = False

        for line in lines:
            # Skip email headers
            if line.startswith(('From:', 'Subject:', 'Date:', 'Organization:',
                                'Lines:', 'Message-ID:', 'NNTP-Posting-Host:',
                                'X-', 'Reply-To:', 'Newsgroups:')):
                continue

            # Skip quoted text (lines starting with >)
            if line.strip().startswith('>'):
                skip_quoted = True
                continue

            # Reset skip_quoted if we hit a non-quoted line
            if skip_quoted and line.strip() and not line.strip().startswith('>'):
                skip_quoted = False

            if not skip_quoted and line.strip():
                # Remove excessive whitespace and special characters
                cleaned_line = re.sub(r'\s+', ' ', line.strip())
                cleaned_lines.append(cleaned_line)

        return '\n'.join(cleaned_lines)

    @staticmethod
    def extract_subject_from_text(text: str) -> Optional[str]:
        """Extract subject line from email text"""
        lines = text.split('\n')
        for line in lines:
            if line.startswith('Subject:'):
                subject = line.replace('Subject:', '').strip()
                # Remove "Re:" prefixes
                subject = re.sub(r'^(Re:\s*)+', '', subject, flags=re.IGNORECASE)
                return subject[:500] if subject else None
        return None

    @staticmethod
    def extract_author_from_text(text: str) -> Optional[str]:
        """Extract author from email text"""
        lines = text.split('\n')
        for line in lines:
            if line.startswith('From:'):
                author = line.replace('From:', '').strip()
                # Extract email or name
                if '<' in author and '>' in author:
                    # Extract name before email
                    name_part = author.split('<')[0].strip()
                    if name_part:
                        return name_part
                    # Fallback to email
                    email_match = re.search(r'<(.+?)>', author)
                    if email_match:
                        return email_match.group(1).split('@')[0]
                else:
                    # Just return the author as is, but limit length
                    return author.split('@')[0] if '@' in author else author
        return None

    @staticmethod
    def load_20newsgroups_data(
            subset: str = 'train',
            categories: Optional[List[str]] = None,
            max_documents: int = 1000,
            remove_headers: bool = True,
            remove_footers: bool = True,
            remove_quotes: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Load data from 20newsgroups dataset

        Args:
            subset: 'train', 'test', or 'all'
            categories: List of categories to load (None for all)
            max_documents: Maximum number of documents to load
            remove_headers: Remove email headers
            remove_footers: Remove email footers
            remove_quotes: Remove quoted text
        """
        try:
            from sklearn.datasets import fetch_20newsgroups

            logger.info(f"Loading 20newsgroups dataset (subset: {subset})")

            # Configure removal parameters
            remove = []
            if remove_headers:
                remove.append('headers')
            if remove_footers:
                remove.append('footers')
            if remove_quotes:
                remove.append('quotes')

            # Load the dataset
            newsgroups = fetch_20newsgroups(
                subset=subset,
                categories=categories,
                remove=tuple(remove) if remove else (),
                shuffle=True,
                random_state=42
            )

            documents = []
            category_names = newsgroups.target_names

            # Process documents
            for i, (text, target) in enumerate(zip(newsgroups.data, newsgroups.target)):
                if i >= max_documents:
                    break

                if not text or not text.strip():
                    continue

                # Get category name
                category = category_names[target]

                # Clean text
                cleaned_text = NewsDataLoader.clean_text(text)
                if len(cleaned_text) < 50:  # Skip very short texts
                    continue

                # Extract subject/title
                title = NewsDataLoader.extract_subject_from_text(newsgroups.data[i])
                if not title:
                    # Use first line as title if no subject found
                    first_lines = cleaned_text.split('\n')[:2]
                    title = ' '.join(first_lines)[:200]
                    if not title:
                        title = f"Post from {category}"

                # Extract author
                author = NewsDataLoader.extract_author_from_text(newsgroups.data[i])
                if not author:
                    author = "Anonymous"

                # Create tags based on category
                tags = [category.replace('.', '-')]
                if 'comp.' in category:
                    tags.append('computer')
                elif 'rec.' in category:
                    tags.append('recreation')
                elif 'sci.' in category:
                    tags.append('science')
                elif 'talk.' in category:
                    tags.append('discussion')
                elif 'soc.' in category:
                    tags.append('society')
                elif 'misc.' in category:
                    tags.append('misc')
                elif 'alt.' in category:
                    tags.append('alternative')

                doc_data = {
                    'title': title,
                    'body': cleaned_text,
                    'category': category,
                    'author': author,
                    'tags': tags,
                    'status': 'active'
                }

                documents.append(doc_data)

            logger.info(f"Loaded {len(documents)} documents from 20newsgroups")
            return documents

        except ImportError:
            logger.error(
                "scikit-learn is required to load 20newsgroups dataset. Install with: pip install scikit-learn")
            return []
        except Exception as e:
            logger.error(f"Failed to load 20newsgroups data: {e}")
            return []

    @staticmethod
    def load_sample_data() -> List[Dict[str, Any]]:
        """Load minimal sample data for testing"""
        return [
            {
                'title': 'Sample Tech Discussion',
                'body': 'This is a sample technology discussion post about computer graphics and hardware.',
                'category': 'comp.graphics',
                'author': 'tech_user',
                'tags': ['comp-graphics', 'computer'],
                'status': 'active'
            },
            {
                'title': 'Space Exploration Update',
                'body': 'Discussion about recent developments in space technology and missions.',
                'category': 'sci.space',
                'author': 'space_enthusiast',
                'tags': ['sci-space', 'science'],
                'status': 'active'
            },
            {
                'title': 'Baseball Season Analysis',
                'body': 'Analysis of the current baseball season and team performances.',
                'category': 'rec.sport.baseball',
                'author': 'sports_fan',
                'tags': ['rec-sport-baseball', 'recreation'],
                'status': 'active'
            }
        ]