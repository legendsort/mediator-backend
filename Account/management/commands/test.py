import django.db
from django.core.management.base import BaseCommand

import Paper.models
from Account.message import Error
from Bank.task import run_fetch_bank_data


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        status = [
            'new submission',
            'Rejected',
            'No Editor Invited',
            'Editor Invited',
            'With Editor',
            'Reviewer Invited',
            'Under Review',
            'Ready for Decision',
            'Decision in Progress',
            'Decision Pending',
            'In Copy Editing',
            'Resubmission Requested',
            'Under Resubmission',
            'Revision Requested',
            'Under Revision',
            'Transfer Suggested',
            'Transferred',
            'Not Transferred',
            'Transferred Draft Revisions',
            'Accepted',
            'Sent to Production',
            'Transmittal Failed',
            'With Journal',
            'Withdrawn',
            'Declined to Resubmit',
            'Declined to Revise',
            'Removed',
            'Expired'
            ]
        for st in status:
            try:
                Paper.models.Status.objects.create(name=st)
            except django.db.DatabaseError as e:
                continue
        # run_fetch_bank_data()
