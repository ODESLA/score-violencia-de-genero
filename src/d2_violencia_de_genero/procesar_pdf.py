import os
import io
import argparse
import logging
from pathlib import Path
from glob import glob

from fuzzysearch import find_near_matches
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import TextConverter

logger = logging.getLogger("main")


def filter_pages(all_pages, dist):
    """
    Function to filter elements of a list based on the max distance allowed between consecutive elements
    Args:
        all_pages: list of integers
        dist: max distance allow between consecutive elements of the all_pages list

    Returns: list af integers that meet the max distance criteria
    """
    new_pages = []
    for i in range(len(all_pages) - 1):
        if (all_pages[i + 1] - all_pages[i]) < dist:
            new_pages.append(all_pages[i])
        elif (i > 0) and (all_pages[i] - all_pages[i - 1] < dist):
            new_pages.append(all_pages[i])
    return new_pages


def extract_text_from_pdf(pdf_path, full=False, pages=()):
    """
    Helper function to extract the plain text from PDF files
    Args:
        pdf_path: path to PDF file to be extracted
        full: optional boolean parameter to indicate if all the pages must be processed
        pages: range of pages that needs to be extracted

    Returns: iterator of string of extracted text
    """

    if full:
        with open(pdf_path, "rb") as pdf:
            for page in PDFPage.get_pages(pdf, caching=True, check_extractable=True):
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
    elif pages:
        with open(pdf_path, "rb") as pdf:
            for page_number, page in enumerate(
                PDFPage.get_pages(pdf, caching=True, check_extractable=True)
            ):
                resource_manager = PDFResourceManager()
                fake_file_handle = io.StringIO()
                converter = TextConverter(resource_manager, fake_file_handle)
                page_interpreter = PDFPageInterpreter(resource_manager, converter)
                if pages[0] <= page_number <= pages[1]:
                    page_interpreter.process_page(page)
                    text = fake_file_handle.getvalue()
                    yield text
                else:
                    yield ""

                    # close open handles
                converter.close()
                fake_file_handle.close()


def extract_information(file):
    path = Path(file)
    # TODO Utilizar OCR cuando no se puede extraer el texto del pdf

    string_1 = "corte suprema de justicia de la nación"
    string_2 = "oficina de violencia doméstica"

    i = 0
    all_pages = []
    for text in extract_text_from_pdf(path, full=True):
        matches_1 = find_near_matches(string_1, text.lower(), max_l_dist=4)
        matches_2 = find_near_matches(string_2, text.lower(), max_l_dist=4)
        if matches_1 and matches_2:
            all_pages.append(i)
        i += 1

    if len(all_pages) > 2:
        all_pages = filter_pages(all_pages, 10)
        all_pages = sorted(all_pages)
        with open(f"{path.stem}.txt", "w", encoding="UTF8", errors="ignore") as f:
            for text in extract_text_from_pdf(
                path, pages=(all_pages[0], all_pages[-1] + 1)
            ):
                if len(text) > 0:
                    f.write("============ page ==============")
                    f.write(text)
    else:
        print("No se encontró ninguna página de la OVD")


def main(file, all_files):

    if file:
        extract_information(file)

    elif all_files:
        path = str(Path(os.getcwd()) / "*.pdf")
        files = glob(path)
        for file in files:
            print(f"procesando {file}")
            extract_information(file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extraer información de la OVD")
    # TODO permitir que se pueda especificar la carpeta a procesar
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        dest="all_files",
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

        if file_path.exists() and Path(file_path).suffix[1:].lower() != "pdf":
            logger.error("El archivo especificado no es un pdf")
            exit(1)

        if not file_path.is_file():
            logger.error("El argumento suministrado no es un archivo válido")
            exit(1)

    if args.file and args.all_files:
        logger.error("Los argumentos suministrados son excluyentes")
        exit(1)

    if not args.file and not args.all_files:
        logger.error("Se debe suministrar al menos un argumento")
        exit(1)

    main(args.file, args.all_files)
