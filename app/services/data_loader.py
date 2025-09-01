# services/data_loader.py
import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Pre-compile regex patterns for efficiency
RE_SUBJECT_PREFIX = re.compile(r'^(Re:\s*)+', re.IGNORECASE)
RE_EMAIL_EXTRACT = re.compile(r'<(.+?)>')
RE_EXCESSIVE_WHITESPACE = re.compile(r'\s+')

# Email headers to skip (as a set for O(1) lookup)
EMAIL_HEADERS = {
    'From:', 'Subject:', 'Date:', 'Organization:', 'Lines:',
    'Message-ID:', 'NNTP-Posting-Host:', 'Reply-To:', 'Newsgroups:'
}


class NewsDataLoader:
    """Load real news data from 20newsgroups dataset"""

    @staticmethod
    def _parse_email_headers(text: str) -> Dict[str, Optional[str]]:
        """Extract common headers from email text in one pass"""
        lines = text.split('\n')
        headers: Dict[str, Optional[str]] = {'subject': None, 'author': None}

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped or ':' not in line_stripped:
                continue

            if line.startswith('Subject:'):
                subject = line[8:].strip()  # len('Subject:') = 8
                if subject:
                    # Remove "Re:" prefixes
                    subject = RE_SUBJECT_PREFIX.sub('', subject)
                    headers['subject'] = subject[:500] if subject else None

            elif line.startswith('From:'):
                author = line[5:].strip()  # len('From:') = 5
                if author:
                    # Extract name or email
                    if '<' in author and '>' in author:
                        # Extract name before email
                        name_part = author.split('<')[0].strip()
                        if name_part:
                            headers['author'] = name_part
                        else:
                            # Fallback to email
                            email_match = RE_EMAIL_EXTRACT.search(author)
                            if email_match:
                                headers['author'] = email_match.group(1).split('@')[0]
                    else:
                        # Just return the author as is, but limit length
                        headers['author'] = author.split('@')[0] if '@' in author else author

        return headers

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and process text content efficiently"""
        if not text:
            return ""

        lines = text.split('\n')
        cleaned_lines = []
        skip_quoted = False

        for line in lines:
            stripped_line = line.strip()  # Call strip() only once per line

            # Skip email headers using set lookup (O(1))
            header_found = False
            for header in EMAIL_HEADERS:
                if line.startswith(header) or (stripped_line.startswith('X-') and ':' in stripped_line):
                    header_found = True
                    break
            if header_found:
                continue

            # Handle quoted text
            if stripped_line.startswith('>'):
                skip_quoted = True
                continue
            elif skip_quoted and stripped_line:
                skip_quoted = False

            if not skip_quoted and stripped_line:
                # Remove excessive whitespace in one regex call
                cleaned_line = RE_EXCESSIVE_WHITESPACE.sub(' ', stripped_line)
                cleaned_lines.append(cleaned_line)

        return '\n'.join(cleaned_lines)

    @staticmethod
    def extract_subject_from_text(text: str) -> Optional[str]:
        """Extract subject line from email text"""
        headers = NewsDataLoader._parse_email_headers(text)
        return headers['subject']

    @staticmethod
    def extract_author_from_text(text: str) -> Optional[str]:
        """Extract author from email text"""
        headers = NewsDataLoader._parse_email_headers(text)
        return headers['author']

    @staticmethod
    def _generate_tags(category: str) -> List[str]:
        """Generate tags based on category efficiently"""
        tags = [category.replace('.', '-')]

        # Use dictionary for O(1) lookup instead of multiple if-elif
        category_mappings = {
            'comp.': 'computer',
            'rec.': 'recreation',
            'sci.': 'science',
            'talk.': 'discussion',
            'soc.': 'society',
            'misc.': 'misc',
            'alt.': 'alternative'
        }

        for prefix, tag in category_mappings.items():
            if category.startswith(prefix):
                tags.append(tag)
                break

        return tags

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
        Load data from 20newsgroups dataset with improved efficiency

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

            logger.info(f"Loading 20newsgroups dataset (subset: {subset}, max_docs: {max_documents})")

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

            # Process documents with enumerate limit for efficiency
            for i, (text, target) in enumerate(zip(newsgroups.data, newsgroups.target)):
                if i >= max_documents:
                    break

                if not text or len(text.strip()) < 50:  # Skip empty or very short texts
                    continue

                category = category_names[target]

                # Clean text
                cleaned_text = NewsDataLoader.clean_text(text)
                if len(cleaned_text) < 50:
                    continue

                # Extract headers in one pass
                headers = NewsDataLoader._parse_email_headers(newsgroups.data[i])

                # Use extracted subject or create fallback title
                title = headers['subject']
                if not title:
                    # Use first line as title if no subject found
                    first_lines = cleaned_text.split('\n')[:2]
                    title = ' '.join(first_lines)[:200]
                    if not title:
                        title = f"Post from {category}"

                # Use extracted author or default
                author = headers['author'] or "Anonymous"

                # Generate tags efficiently
                tags = NewsDataLoader._generate_tags(category)

                doc_data = {
                    'title': title,
                    'body': cleaned_text,
                    'category': category,
                    'author': author,
                    'tags': tags,
                    'status': 'active'
                }

                documents.append(doc_data)

            logger.info(f"Successfully loaded {len(documents)} documents from 20newsgroups")
            return documents

        except ImportError:
            logger.error(
                "scikit-learn is required to load 20newsgroups dataset. Install with: pip install scikit-learn"
            )
            return []
        except Exception as e:
            logger.error(f"Failed to load 20newsgroups data: {e}")
            return []

    @staticmethod
    def load_sample_data() -> List[Dict[str, Any]]:
        """Load minimal sample data for testing - with more variety"""
        return [
            {
                'title': 'Advanced Graphics Rendering Techniques',
                'body': 'Discussion about modern computer graphics rendering techniques including ray tracing, rasterization, and GPU optimization strategies for real-time applications.',
                'category': 'comp.graphics',
                'author': 'graphics_dev',
                'tags': ['comp-graphics', 'computer', 'rendering'],
                'status': 'active'
            },
            {
                'title': 'Mars Rover Latest Discoveries',
                'body': 'Recent findings from the Mars rover mission including geological samples, atmospheric readings, and potential signs of ancient microbial life.',
                'category': 'sci.space',
                'author': 'mars_researcher',
                'tags': ['sci-space', 'science', 'mars'],
                'status': 'active'
            },
            {
                'title': 'World Series Predictions and Analysis',
                'body': 'Comprehensive analysis of the current baseball season statistics, team performance metrics, and predictions for the upcoming World Series.',
                'category': 'rec.sport.baseball',
                'author': 'baseball_analyst',
                'tags': ['rec-sport-baseball', 'recreation', 'statistics'],
                'status': 'active'
            },
            {
                'title': 'Quantum Cryptography Breakthrough',
                'body': 'New developments in quantum key distribution and post-quantum cryptographic algorithms that could revolutionize secure communications.',
                'category': 'sci.crypt',
                'author': 'crypto_expert',
                'tags': ['sci-crypt', 'science', 'quantum'],
                'status': 'active'
            },
            {
                'title': 'Electric Vehicle Market Trends',
                'body': 'Analysis of the current electric vehicle market, battery technology improvements, and consumer adoption patterns across different regions.',
                'category': 'rec.autos',
                'author': 'auto_journalist',
                'tags': ['rec-autos', 'recreation', 'electric'],
                'status': 'active'
            }
        ]