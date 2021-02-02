# website-publications

Repository dedicated to the [MT-UPC publication website](https://mt.cs.upc.edu/publications). Helps to create and maintain publications and how they are displayed on the webpage.

### Dependencies
```pip install -r requirements.txt```

### Execution
1. Add new or update existing bib entries in the `publication_files/publications.bib`.
2. Generate `publication_files/publications.html` by running the script:
```
python bib2html.py \
    --i publication_files/publications.bib \
    --o publication_files/publications.html
```