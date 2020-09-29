import os
import io
import argparse
import logging
from pathlib import Path
from glob import glob

from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import TextConverter

logger = logging.getLogger("main")



def extract_text_from_pdf(pdf_path):
    """
    Helper function to extract the plain text from .pdf files

    :param pdf_path: path to PDF file to be extracted
    :return: iterator of string of extracted text
    """
    with open(pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            resource_manager = PDFResourceManager()
            fake_file_handle = io.StringIO()
            converter = TextConverter(resource_manager, fake_file_handle)
            page_interpreter = PDFPageInterpreter(resource_manager, converter)
            page_interpreter.process_page(page)

            text = fake_file_handle.getvalue()
            yield text

            # close open handles
            converter.close()
            fake_file_handle.close()


def extract_information(file):
    path = Path(file)
    # TODO Mejorar la lógica para detectar las páginas con el copete. Sugerencia: usar Regex

    string1 = 'Corte Suprema de Justicia de la Nación'
    string2 = 'Oficina de Violencia Doméstica'

    with open(f'{path.stem}.txt', 'w', encoding='UTF8', errors='ignore') as f:
        i = 1
        for text in extract_text_from_pdf(path):
            if string1 in text and string2 in text:
                f.write(text)
                f.write(f'============ page {i} ==============')
                i += 1


def main(file, all_files):

    if file:
        extract_information(file)

    elif all_files:
        path = str(Path(os.getcwd()) / "*.pdf")
        files = glob(path)
        for file in files:
            print(f'procesando {file}')
            extract_information(file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extraer información de la OVD"
    )
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        dest='all_files',
        default=False,
        required=False,
        help="Process all files in the root folder",
    )
    parser.add_argument(
        "-f",
        "--file",
        required=False,
        dest="file",
        help="File to be processed",
    )

    args = parser.parse_args()

    if args.file:
        file_path = Path(args.file)

        if not file_path.exists():
            logger.error("El archivo no existe")
            exit(1)

        if file_path.exists() and Path(file_path).suffix[1:].lower() != 'pdf':
            logger.error("El archivo especificado no es un pdf")
            exit(1)

        if not file_path.is_file():
            logger.error("El argumento suministrado no es un archivo válido")
            exit(1)

    if args.file and args.all_files:
        logger.error('Los argumentos suministrados son excluyentes')
        exit(1)

    if not args.file and not args.all_files:
        logger.error('Se debe suministrar al menos un argumento')
        exit(1)

    main(args.file, args.all_files)