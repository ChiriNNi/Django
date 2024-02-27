from datetime import datetime, timedelta

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import DateTimeRangeField, ArrayField, HStoreField, CICharField # , JSONField
from django.contrib.postgres.indexes import GistIndex
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import RangeOperators
from django.contrib.postgres.validators import (RangeMinValueValidator, RangeMaxValueValidator, KeysValidator)
from django.db.models import JSONField
from django.db import models
from django.contrib.auth.models import User


class AdvUser(models.Model):
    is_activated = models.BooleanField(default=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Spare(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return f'{self.name}'


class Machine(models.Model):
    name = models.CharField(max_length=30)
    spares = models.ManyToManyField(Spare, through='Kit',
                                    through_fields=('machine', 'spare'))
    notes = GenericRelation('Note')

    def __str__(self):
        return f'{self.name}'


class MachinePrice(Machine):
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_total_price(self):
        total_price = self.price + sum(kit.spare.price for kit in self.kit_set.all())
        return total_price


class MachineMaintenance(MachinePrice):
    def create_maintenance_schedule(self, start_date=None):
        if start_date is None:
            start_date = datetime.now().date()

        price = self.price

        if price <= 1000:
            interval_in_months = 12
        elif 1000 < price <= 5000:
            interval_in_months = 6
        else:
            interval_in_months = 3

        maintenance_dates = []
        maintenance_dates.append(start_date)

        for i in range(1, 12):
            next_date = start_date + timedelta(days=i * 30 * interval_in_months)
            maintenance_dates.append(next_date)

        schedule_text = ', '.join(date.strftime('%Y-%m-%d') for date in maintenance_dates)

        self.maintenance_schedule = schedule_text
        self.save()

        return schedule_text


class Kit(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    spare = models.ForeignKey(Spare, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=0)


class Note(models.Model):
    content = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class Message(models.Model):
    content = models.TextField()


class PrivateMessage(Message):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.OneToOneField(Message, on_delete=models.CASCADE, parent_link=True)


class PGSRoomReserving(models.Model):
    name = models.CharField(max_length=20, verbose_name='Помещение')
    reserving = DateTimeRangeField( verbose_name='Время резервирования',
                                    validators=[RangeMinValueValidator(limit_value=datetime(2000, 1, 1)),
                                                RangeMaxValueValidator(limit_value=datetime(3000, 1, 1)),])
    cancelled = models.BooleanField(default=False, verbose_name='Отменить резервирование')

    class Meta:
        indexes = [
            GistIndex(fields=['reserving'],
                      name='i_pgsrr_reserving',
                      opclasses=('range_ops',),
                      fillfactor=50)
        ]

        constraints = [
            ExclusionConstraint(name='c_pgsrr_reserving',
                                expressions=[('name', RangeOperators.EQUAL),
                                             ('reserving', RangeOperators.OVERLAPS)],
                                condition=models.Q(cancelled=False))
        ]


class PGSRubric(models.Model):
    name = models.CharField(max_length=20, verbose_name='Имя')
    description = models.TextField(verbose_name='Описание')
    tags = ArrayField(base_field=models.CharField(max_length=20), verbose_name='Теги')

    class Meta:
        indexes = [
            models.Index(fields=('name', 'description'),
                         name='i_pgsrubric_name_description',
                         opclasses=('varchar_pattern_ops', 'bpchar_pattern_ops'))
        ]

        constraints = [ExclusionConstraint(name='c_pgsrubric_name_description',
                                           expressions=[('name', RangeOperators.EQUAL),
                                                        ('description', RangeOperators.EQUAL)])
                       ]


class PGSProject(models.Model):
    name = models.CharField(max_length=40, verbose_name='Название')
    platforms = ArrayField(base_field=ArrayField(
      base_field=models.CharField(max_length=20)),
      verbose_name='Использованные платформы'
    )


class PSGProject2(models.Model):
    name = models.CharField(max_length=40, verbose_name='Название')
    platforms = HStoreField(verbose_name='Использованные платформы',
                            validators=[KeysValidator(('client', 'server'),
                                                      strict=True)])


class PSGProject3(models.Model):
    name = CICharField(max_length=40, verbose_name='Название')
    data = JSONField()



