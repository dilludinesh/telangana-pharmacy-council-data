import textwrap

from bs4 import BeautifulSoup

from reader import Reader


def build_table(html: str):
    soup = BeautifulSoup(textwrap.dedent(html), "html.parser")
    return soup.find("table")


def test_parse_basic_table_extracts_records():
    table = build_table(
        """
        <table id="tablesorter-demo">
          <tr>
            <th>S.No</th><th>Reg</th><th>Name</th><th>Father</th><th>Category</th>
          </tr>
          <tr>
            <td>1</td><td>TG000001</td><td>Alice</td><td>Bob</td><td>BPharm</td>
          </tr>
          <tr>
            <td>002</td><td>TG000002</td><td>Charlie</td><td>Dan</td><td>DPharm</td>
          </tr>
        </table>
        """
    )

    records = Reader.parse_basic_table(table)

    assert records == [
        {
            "serial_number": 1,
            "registration_number": "TG000001",
            "name": "Alice",
            "father_name": "Bob",
            "category": "BPharm",
        },
        {
            "serial_number": 2,
            "registration_number": "TG000002",
            "name": "Charlie",
            "father_name": "Dan",
            "category": "DPharm",
        },
    ]


def test_parse_basic_table_handles_missing_rows():
    table = build_table(
        """
        <table>
          <tr><th>Header</th></tr>
          <tr><td>Insufficient</td></tr>
        </table>
        """
    )

    records = Reader.parse_basic_table(table)
    assert records == []
