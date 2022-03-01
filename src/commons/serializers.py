from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers
from rest_framework_api_key.permissions import HasAPIKey

from commons.models import CustomerInfo, Address, BankAccount
from commons.utils.ssn import SsnParser


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['postcode', 'address', 'address_detail']


class CustomerInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerInfo
        fields = ['id', 'email', 'name', 'cellphone', 'birthdate', 'ssn', 'address', 'extra_1', 'extra_2', 'extra_3']
        read_only_fields = ['id']

    address = AddressSerializer(many=False, required=False)

    def create(self, validated_data):
        address_data = validated_data.pop('address', None)
        customer_info = CustomerInfo(**validated_data)
        if address_data:
            address = Address.objects.create(**address_data)
            customer_info.address = address
        customer_info.save()
        return customer_info


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = ['id', 'bank_code', 'bank_name', 'account_no', 'account_name', 'ssn', 'checked', 'result_msg',
                  'account_name_check']
        read_only_fields = ['id', 'bank_name', 'checked', 'result_msg']

    account_name_check = serializers.BooleanField(required=False, default=False, write_only=True)
    bank_name = serializers.SerializerMethodField()

    def validate_ssn(self, value):
        if value is None:
            return value
        try:
            parser = SsnParser(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        else:
            return parser.ssn

    def validate_bank_code(self, value):
        value = str(value)
        if value not in [bank[0] for bank in BankAccount.BANK_CODE_CHOICES]:
            raise serializers.ValidationError(f"{value}는 존재하지 않는 은행 코드입니다.")
        return value

    def validate_account_name(self, value):
        return value.strip()

    def get_bank_name(self, obj):
        return obj.get_bank_code_display()

    def to_representation(self, instance):
        rep = super(BankAccountSerializer, self).to_representation(instance)
        rep['ssn'] = SsnParser(rep['ssn']).masked_ssn
        return rep

    def create(self, validated_data):
        account_name_check = validated_data.pop('account_name_check', False)
        base_affiliate = self.context.get('base_affiliate', None)
        validated_data['base_affiliate'] = base_affiliate
        account = super(BankAccountSerializer, self).create(validated_data)
        if account_name_check:
            account._account_name_check()
        else:
            account.checked = None
            account.result_msg = "예금주명 미확인"
            account.check_datetime = account.registered_at
            account.save()
        self.instance = account
        return account


class AESSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=((0, '암호화'), (1, '복호화')), required=True)
    key = serializers.CharField(required=True, max_length=32, min_length=32)
    iv = serializers.CharField(required=False, max_length=16, min_length=16, allow_null=True, allow_blank=False)
    data = serializers.CharField(required=True, max_length=1000, allow_null=False, allow_blank=False)
