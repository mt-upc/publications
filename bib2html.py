import argparse
import calendar
from collections import OrderedDict
from operator import itemgetter 
from pybtex.database import parse_file
from pybtex.richtext import Text
from tqdm import tqdm

months_abbr = {month.lower(): index for index, month in enumerate(calendar.month_abbr) if month}
months_full = {month.lower(): index for index, month in enumerate(calendar.month_name) if month}

class Citation(object):
    def __init__(self, bib_entry):
        if bib_entry.persons.get('author'):
            self.authors = self.get_authors(bib_entry.persons['author'])
            self.first_surname = self.get_first_surname(bib_entry.persons['author']) 
        else:
            self.authors = self.get_authors(bib_entry.persons['editor'])
            self.first_surname = self.get_first_surname(bib_entry.persons['editor'])
        self.title = bib_entry.fields.get('title', None)
        self.year = bib_entry.fields.get('year', None)
        self.month = bib_entry.fields.get('month', 'jan')
        self.month_idx = months_abbr[self.month.lower()] if self.month.lower() in months_abbr else months_full[self.month.lower()]
        self.address = bib_entry.fields.get('address', None)
        self.pages = bib_entry.fields.get('pages', None)
        self.journal = bib_entry.fields.get('journal', None)
        self.volume = bib_entry.fields.get('volume', None)
        self.number = bib_entry.fields.get('number', None)
        self.booktitle = bib_entry.fields.get('booktitle', None)
        self.editor = bib_entry.fields.get('editor', None)
        self.publisher = bib_entry.fields.get('publisher', None)
        self.organization = bib_entry.fields.get('organization', None)
        self.url = bib_entry.fields.get('url', None)
        self.doi = bib_entry.fields.get('doi', None)
        self.bibtex = bib_entry.to_string('bibtex')

    def get_authors(self, persons) -> str:
        return str(', '.join(author for author in self.get_authors_list(persons)))
    
    def get_authors_list(self, persons) -> list:
        authors = []
        for person in persons:
            author = person.rich_first_names
            author += person.rich_middle_names
            author += person.rich_last_names
            author_str = ' '.join(str(a) for a in author)
            authors.append(author_str)
        return authors

    def get_first_surname(self, persons) -> str:
        return str(persons[0].rich_last_names[0])

def generate_citations(bib_data) -> list:
    citations = []
    for entry_id in tqdm(bib_data.entries):
        citation = Citation(bib_data.entries[entry_id])
        citation_dict = {'year': int(citation.year), 'month': citation.month_idx, 'first_author': citation.first_surname, 'id': entry_id, 'citation': citation}
        citations.append(citation_dict)
    return citations

def save_html(html_file, citations):
    with open(html_file, 'w') as out_file:
        curr_year = 0
        sorted_citations = sorted(citations, key=lambda k: (-k['year'], -k['month'], k['first_author']))
        
        for element in tqdm(sorted_citations):
            if curr_year != element['year']:
                if curr_year != 0:
                    out_file.write('</br></br>\n')
                curr_year = element['year']
                out_file.write('<div style="width:95%; margin: 0 auto 0 auto;">\n')
                out_file.write('\t<h3 class>{}</h3>\n'.format(curr_year))
                out_file.write('</div>\n')

            out_file.write(f'<div id="refs" style="width: 92%; margin: 0 auto 0 auto;">\n')
            out_file.write('\t<div class="h-row-container gutters-row-lg-1 gutters-row-md-1 gutters-row-0 gutters-row-v-lg-1 gutters-row-v-md-1 gutters-row-v-1 style-641 style-local-2180-c27 position-relative">\n')
            out_file.write('\t\t<div style="color: #778899 !important;"><strong>{}</strong></div>\n'.format(element['citation'].authors))
            if element['citation'].url:
                title = remove_latex_chars(element['citation'].title)
                url = '"' + element['citation'].url + '"'
                out_file.write('\t\t<div><a href={} target="_blank"><strong>{}</strong></a></div>\n'.format(url, title))
            else:
                out_file.write('\t\t<div>{}</div>\n'.format(element['citation'].title))
            if element['citation'].journal:
                journal = remove_latex_chars(element['citation'].journal)
                if element['citation'].volume:
                    journal += ', ' + element['citation'].volume
                journal += ' (' + element['citation'].year + ')'
                if element['citation'].pages:
                    journal += ', ' + element['citation'].pages
                out_file.write('\t\t<div style="font-style: italic;">{}</div>\n'.format(journal))
            if element['citation'].booktitle:
                conference = remove_latex_chars(element['citation'].booktitle)
                conference += ' (' + element['citation'].year + ')'
                out_file.write('\t\t<div style="font-style: italic;">{}</div>\n'.format(conference))
            out_file.write('\t</div>\n')
            out_file.write('</div>\n')

def remove_latex_chars(text) -> str:
    return text.translate(str.maketrans('', '', "{}"))

def get_args():
    parser = argparse.ArgumentParser(description='Filter out sentences')
    parser.add_argument('-i', '--input-file', type=str, required=True, help='Input .bib file')
    parser.add_argument('-o', '--output-file', type=str, required=True, help='Output .html file ready to be copied & pasted to the Publications page')
    return parser.parse_args()

def main():
    args = get_args()
    print("Parsing %s file..." % args.input_file)
    bib_data = parse_file(args.input_file)
    print('Generating %i citations...' % len(bib_data.entries))
    citations = generate_citations(bib_data)
    print("Saving %s file..." % args.output_file)
    save_html(args.output_file, citations)

if __name__ == '__main__':
    main()
