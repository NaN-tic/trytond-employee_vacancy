import datetime
import unittest

from dateutil.relativedelta import relativedelta
from proteus import Model, Wizard
from trytond.modules.company.tests.tools import create_company, get_company
from trytond.tests.test_tryton import drop_db
from trytond.tests.tools import activate_modules


class Test(unittest.TestCase):

    def setUp(self):
        drop_db()
        super().setUp()

    def tearDown(self):
        drop_db()
        super().tearDown()

    def test(self):

        # Imports

        # Install asset_maintenance
        activate_modules('employee_vacancy')

        # Create company
        _ = create_company()
        company = get_company()

        # Create a party
        Party = Model.get('party.party')
        party = Party(name='Customer')
        party.save()
        party2 = Party(name='Customer')
        party2.save()

        # Create an employee
        Employee = Model.get('company.employee')
        employee = Employee()
        employee.party = party
        employee.company = company
        employee.save()

        # Create a phase
        CandidatePhase = Model.get('employee.candidate.phase')
        phase = CandidatePhase()
        phase.name = 'Phase'
        phase.save()

        # Create vacancy
        Vacancy = Model.get('employee.vacancy')
        vacancy = Vacancy()
        vacancy.name = 'Vacancy'
        vacancy.employee = employee
        vacancy.description = 'We have a vacancy.'
        vacancy.start = datetime.date.today() - relativedelta(days=15)
        vacancy.end = datetime.date.today()
        vacancy.save()

        # Create a candidate
        Candidate = Model.get('employee.candidate')
        candidate = Candidate()
        candidate.vacancy = vacancy
        candidate.party = party
        candidate.phase = phase
        candidate.save()

        # Create resume
        Resume = Model.get('employee.resume')
        resume = Resume()
        resume.party = party
        resume.save()

        # Create level
        Level = Model.get('employee.education.level')
        level = Level()
        level.name = 'Level'
        level.save()

        # Create resume education
        ResumeEducation = Model.get('employee.resume.education')
        education = ResumeEducation()
        education.resume = resume
        education.level = level
        education.school = party
        education.save()

        # Try replace active party
        replace = Wizard('party.replace', models=[party])
        replace.form.source = party
        replace.form.destination = party2
        replace.execute('replace')

        # Check fields have been replaced
        candidate.reload()
        self.assertEqual(candidate.party, party2)
        resume.reload()
        self.assertEqual(resume.party, party2)
        education.reload()
        self.assertEqual(education.school, party2)
