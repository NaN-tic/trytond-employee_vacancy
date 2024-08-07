import datetime
import unittest

from dateutil.relativedelta import relativedelta
from proteus import Model
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

        # Create database
        config = activate_modules('employee_vacancy')

        # Create company
        _ = create_company()
        company = get_company()

        # Create employee
        Party = Model.get('party.party')
        party = Party(name='Employee')
        party.save()
        Employee = Model.get('company.employee')
        employee = Employee()
        employee.party = party
        employee.company = company
        employee.save()

        # Create vacancy administrator user
        User = Model.get('res.user')
        Group = Model.get('res.group')
        vacancy_admin_user = User()
        vacancy_admin_user.name = 'Vacancy Administrator'
        vacancy_admin_user.login = 'vacancy_admin'
        vacancy_admin_group, = Group.find([('name', '=',
                                            'Employee Vacancy Administration')])
        vacancy_admin_user.groups.append(vacancy_admin_group)
        vacancy_admin_user.save()

        # Create vacancy user
        User = Model.get('res.user')
        Group = Model.get('res.group')
        vacancy_user = User()
        vacancy_user.name = 'Vacancy'
        vacancy_user.login = 'vacancy'
        vacancy_group, = Group.find([('name', '=', 'Employee Vacancy')])
        vacancy_user.groups.append(vacancy_group)
        Employee = Model.get('company.employee')
        Party = Model.get('party.party')
        employee_party = Party(name='Employee')
        employee_party.save()
        employee = Employee(party=employee_party)
        employee.save()
        vacancy_user.employees.append(employee)
        vacancy_user.employee = employee
        vacancy_user.save()

        # Set admin as current user
        config.user = vacancy_admin_user.id

        # Create candidate phase
        CandidatePhase = Model.get('employee.candidate.phase')
        phase = CandidatePhase()
        phase.name = 'Pending'
        phase.save()

        # Set current user
        config.user = vacancy_user.id

        # Create party
        Party = Model.get('party.party')
        party_candidate_a = Party(name='Candidate A')
        party_candidate_a.save()
        party_candidate_b = Party(name='Candidate B')
        party_candidate_b.save()

        # Create resume
        Resume = Model.get('employee.resume')
        resume_a = Resume(party=party_candidate_a, )
        resume_a.birthdate = datetime.date.today() - relativedelta(year=22)
        resume_a.age = 22
        resume_a.save()

        # Create vacancy
        Vacancy = Model.get('employee.vacancy')
        Url = Model.get('employee.vacancy.url')
        vacancy = Vacancy()
        vacancy.name = 'Vacancy'
        vacancy.employee = employee
        vacancy.description = 'We have a vacancy.'
        vacancy.start = datetime.date.today() - relativedelta(days=15)
        vacancy.end = datetime.date.today()
        url = Url()
        url.url = 'https://linkedin.com'
        vacancy.urls.append(url)
        vacancy.save()

        # Create candidates
        Candidate = Model.get('employee.candidate')
        candidate_a = Candidate()
        candidate_a.vacancy = vacancy
        candidate_a.party = party_candidate_a
        candidate_a.phase = phase
        self.assertEqual(candidate_a.resume, resume_a)
        candidate_a.save()
        candidate_b = Candidate()
        candidate_b.vacancy = vacancy
        candidate_b.party = party_candidate_b
        candidate_b.phase = phase
        self.assertEqual(candidate_b.resume, None)
        candidate_b.save()
