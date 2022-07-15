from docx import *
from docx.shared import *
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT, WD_BREAK
from docx.oxml.ns import qn
from django.apps import apps
import datetime
import os
from django.conf import settings
import zipfile
from os.path import basename
from Account.services import GatewayService


class SubmissionService:
    def __init__(self, submit):
        self.DOCUMENT_ROOT_PATH = '/'.join([
            getattr(settings, 'MEDIA_ROOT', '/media'),
            'submissions',
            str(submit.id)
        ])
        self.submit = submit
        self.document = Document()
        section = self.document.sections[0]
        section.page_height = Mm(297)
        section.page_width = Mm(210)
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(2)
        section.right_margin = Cm(2)
        self.document_name = f"{self.submit.id}__{self.submit.title}.docx"
        self.document_path = '/'.join([
            self.DOCUMENT_ROOT_PATH,
            self.document_name
        ])
        self.zip_file_path = f"{self.DOCUMENT_ROOT_PATH}/{str(self.submit.id)}.zip"

    def create_information_document(self):
        styles = self.document.styles
        left_style = styles.add_style('leftmatch', WD_STYLE_TYPE.PARAGRAPH)
        left_style.font.name = u'arial'
        left_style.font.size = Pt(12)
        left_style.paragraph_format.space_after = Pt(1)
        records = (
            (3, '101', 'Spam'),
            (7, '422', 'Eggs'),
            (4, '631', 'Spam, spam, eggs, and spam')
        )
        table = self.document.add_table(rows=1, cols=3)
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Qty'
        hdr_cells[1].text = 'Id'
        hdr_cells[2].text = 'Desc'
        for qty, id, desc in records:
            row_cells = table.add_row().cells
            row_cells[0].text = str(qty)
            row_cells[1].text = id
            row_cells[2].text = desc
        self.save_document()

    def save_document(self):
        try:
            self.create_folder()
            if os.path.exists(self.document_path):
                os.remove(self.document_path)
            self.document.save(self.document_path)
            return True
        except Exception as e:
            print(e)
            return False

    def create_folder(self):
        try:
            if not os.path.isdir(self.DOCUMENT_ROOT_PATH):
                os.mkdir(self.DOCUMENT_ROOT_PATH)
        except Exception as e:
            print('create folder error', e)

    def zip_data(self):
        print('----', self.zip_file_path)
        with zipfile.ZipFile(self.zip_file_path, 'w') as zipObj:
            zipObj.write(self.document_path, basename(self.document_name))
            for file in self.submit.get_upload_files():
                zipObj.write(file.file.path, basename(file.name))
            zipObj.close()
            return True

    def send(self):
        self.create_information_document()
        self.zip_data()
        try:
            request_zip_file_path = f"{getattr(settings, 'NIS_SEND_DIR_PATH')}/{basename(self.zip_file_path)}"
            if os.path.exists(request_zip_file_path):
                os.remove(request_zip_file_path)
            os.rename(self.zip_file_path, request_zip_file_path)
            gateway_service = GatewayService()
            remote_user_root_path = getattr(settings, 'REMOTE_NEXTCLOUD_USER_ROOT_PATH')
            request_data = {
                'upload_path': f"{remote_user_root_path}/{self.submit.dealer.username}" if self.submit.dealer else '',
                'file_name': basename(self.zip_file_path)
            }
            return gateway_service.send_request(action='upload_resource', data=request_data)
        except Exception as e:
            print('send_error', e)
            return False

