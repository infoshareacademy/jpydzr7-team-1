# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class DataTransaction(models.Model):
    id_user = models.ForeignKey('Users', on_delete=models.CASCADE, db_column='id_user')
    data_transaction = models.DateField()
    income = models.FloatField(blank=True, null=True)
    expense = models.FloatField(blank=True, null=True)
    description = models.CharField(blank=True, null=True)
    category = models.IntegerField(blank=True, null=True)
    transaction_type = models.CharField(blank=True, null=True)

    class Meta:
        db_table = 'DATA_TRANSACTION'


class Families(models.Model):
    family_id = models.AutoField(primary_key=True)
    family_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'FAMILIES'


class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    email = models.EmailField(unique=True, max_length=255)
    login = models.CharField(unique=True, max_length=255)
    password = models.CharField(max_length=255)
    family= models.ForeignKey(Families, models.DO_NOTHING, blank=True, null=True)
    parent_id = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'USERS'
