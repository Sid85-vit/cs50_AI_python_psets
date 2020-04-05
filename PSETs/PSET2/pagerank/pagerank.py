import os
import random
import re
import sys
import numpy as np

DAMPING = 0.85
SAMPLES = 10000
EPSILON = 0.001


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    all_pages = corpus.keys()
    direct_links = corpus[page]
    if (direct_links == {}):
        return dict(zip(all_pages, np.ones(len(all_pages), dtype=np.float)/float(len(all_pages))))
    direct_weights = damping_factor * np.ones(len(direct_links), dtype=np.float)/float(len(direct_links))
    output = dict(zip(direct_links,direct_weights))
    # I can do this much cleaner with np then doing the dict and zip later
    rest = set(all_pages) - set(direct_links)
    for page in rest:
        output[page] = 0.0
    addition = float((1-damping_factor)/len(all_pages))
    sum = 0.0
    for page in output:
        output[page] += addition
        sum += output[page]
    print(f"sum: {sum}")
    return output


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    keys = corpus.keys()
    output = dict(zip(keys, np.zeros(len(keys), dtype=np.float)))
    page = random.choice(keys)
    # gotta make this more efficient
    for i in range(n):
        distribution = transition_model(corpus, page, damping_factor)

    for k in output:
        ouput[k] /= n
    return ouput


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    raise NotImplementedError


if __name__ == "__main__":
    main()
