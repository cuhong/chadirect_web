from django.contrib.auth.hashers import make_password, check_password
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from car_cms.exceptions.accounts import CarCMSAccountError
from car_cms.models import Compare, Account, Estimate, EstimateDetail, ContractRequest, Notice
from customer.models import ProtectedCustomerInfo
from pytz import timezone as tz_timzone
from dateutil.relativedelta import relativedelta

KST = tz_timzone('Asia/Seoul')


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'username', 'name', 'cellphone']


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'username', 'name']


class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'username', 'name', 'cellphone']


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = [
            'username', 'password1', 'password2', 'name', 'cellphone', 'company_slug', 'name_card'
        ]

    password1 = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    password2 = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    company_slug = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    name_card = Base64ImageField(required=True, allow_null=False)

    def validate(self, attrs):
        if attrs.get('password1') != attrs.get('password2'):
            raise ValidationError('비밀번호가 일치하지 않습니다.')
        return attrs


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    password = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    company_slug = serializers.CharField(required=True, allow_null=False, allow_blank=False)

    def authenticate(self):
        from car_cms.models import Account
        data = self.validated_data
        username = data.get('username')
        raw_password = data.get('password')
        company_slug = data.get('company_slug')
        try:
            account = Account.objects.select_related('company').get(
                company__slug=company_slug, username=username
            )
            is_password_correct = check_password(raw_password, account.password)
            if is_password_correct is False:
                raise CarCMSAccountError(1)
            if account.is_active is False:
                raise CarCMSAccountError(3)
            if account.company.is_active is False:
                raise CarCMSAccountError(4)
        except Account.DoesNotExist:
            raise CarCMSAccountError(0)
        return account


class CustomerInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProtectedCustomerInfo
        fields = ['name', 'ssn', 'cellphone']

    ssn = serializers.SerializerMethodField()

    def get_ssn(self, obj):
        return obj.masked_full_ssn


class CompareRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compare
        fields = [
            'name',
            'ssn_prefix',
            'ssn_suffix',
            'cellphone',
            'attach_1',
            'attach_2',
            'attach_3',
            'driver_range',
            'memo'
        ]

    # customer = CompareCustomerInfoSerializer()

    name = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    ssn_prefix = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    ssn_suffix = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    cellphone = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    attach_1 = Base64ImageField(required=True, allow_null=False)
    attach_2 = Base64ImageField(required=False, allow_null=True)
    attach_3 = Base64ImageField(required=False, allow_null=True)

    def validate_name(self, value):
        if value is None:
            raise serializers.ValidationError('성명은 필수 항목입니다.')
        return value

    def validate_ssn_prefix(self, value):
        value = "".join([v for v in value if v.isdigit()])
        if len(value) != 6:
            raise serializers.ValidationError('주민번호 앞자리는 6자리 숫자 입니다.')
        if value is None:
            raise serializers.ValidationError('주민번호 앞자리는 필수 항목입니다.')
        return value

    def validate_ssn_suffix(self, value):
        value = "".join([v for v in value if v.isdigit()])
        if len(value) != 7:
            raise serializers.ValidationError('주민번호 뒷자리는 7자리 숫자 입니다.')
        if value is None:
            raise serializers.ValidationError('주민번호 뒷자리는 필수 항목입니다.')
        return value

    def validate_cellphone(self, value):
        value = "".join([v for v in value if v.isdigit()])
        if len(value) not in [11, 10]:
            raise serializers.ValidationError("휴대전화번호는 10, 11자리의 숫자입니다.")
        if value is None:
            raise serializers.ValidationError('휴대전화번호는 필수 항목입니다.')
        return value

    def create(self, validated_data):
        customer = ProtectedCustomerInfo.objects.create_customer(
            name=validated_data.get('name'),
            ssn_prefix=validated_data.get('ssn_prefix'),
            ssn_suffix=validated_data.get('ssn_suffix'),
            cellphone=validated_data.get('cellphone'),
        )
        compare = Compare.objects.create(
            account=self.context.get('user'),
            customer=customer,
            driver_range=validated_data.get('driver_range'),
            attach_1=validated_data.get('attach_1'),
            attach_2=validated_data.get('attach_2'),
            attach_3=validated_data.get('attach_3'),
        )
        self.instance = compare
        return compare


class EstimateDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstimateDetail
        fields = [
            'id', 'insurer', 'insurer_display', 'premium', 'memo'
        ]

    insurer_display = serializers.SerializerMethodField()

    def get_insurer_display(self, obj):
        return obj.get_insurer_display()


class EstimateRepresentationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estimate
        fields = [
            'id', 'registered_at', 'manager', 'insured_name',
            'birthdate',
            'car_no',
            'car_name',
            'start_at',
            'driver_range',
            'driver_range_display',
            'min_age',
            'bi_2',
            'bi_2_display',
            'li',
            'li_display',
            'self_injury',
            'self_injury_display',
            'uninsured',
            'uninsured_display',
            'self_damage',
            'self_damage_display',
            'emergency',
            'emergency_display',
            'blackbox',
            'blackbox_display',
            'image',
            'estimatedetail_set'
        ]

    manager = ManagerSerializer()
    driver_range_display = serializers.SerializerMethodField()
    bi_2_display = serializers.SerializerMethodField()
    li_display = serializers.SerializerMethodField()
    self_injury_display = serializers.SerializerMethodField()
    uninsured_display = serializers.SerializerMethodField()
    self_damage_display = serializers.SerializerMethodField()
    emergency_display = serializers.SerializerMethodField()
    blackbox_display = serializers.SerializerMethodField()
    estimatedetail_set = EstimateDetailSerializer(many=True)

    def to_representation(self, instance):
        rep = super(EstimateRepresentationSerializer, self).to_representation(instance)
        # rep['registered_at'] = instance.registered_at.strftime("%Y-%m-%d %H:%M:%S")
        rep['registered_at'] = (instance.registered_at + relativedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")
        rep['birthdate'] = instance.birthdate.strftime("%Y-%m-%d")
        rep['start_at'] = instance.start_at.strftime("%Y-%m-%d")
        return rep

    def get_driver_range_display(self, instance):
        return instance.get_driver_range_display()

    def get_bi_2_display(self, instance):
        return instance.get_bi_2_display()

    def get_li_display(self, instance):
        return instance.get_li_display()

    def get_self_injury_display(self, instance):
        return instance.get_self_injury_display()

    def get_uninsured_display(self, instance):
        return instance.get_uninsured_display()

    def get_self_damage_display(self, instance):
        return instance.get_self_damage_display()

    def get_emergency_display(self, instance):
        return instance.get_emergency_display()

    def get_blackbox_display(self, instance):
        return instance.get_blackbox_display()


class ContractRequestRepresentationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractRequest
        fields = [
            'registered_at',
            'estimate_detail', 'msg'
        ]

    estimate_detail = EstimateDetailSerializer()

    def to_representation(self, instance):
        rep = super(ContractRequestRepresentationSerializer, self).to_representation(instance)
        rep['registered_at'] = (instance.registered_at + relativedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")
        return rep


class CompareListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compare
        fields = [
            'id', 'registered_at', 'serial', 'manager', 'customer', 'status',
            'status_display'
        ]

    customer = CustomerInfoSerializer()
    status_display = serializers.SerializerMethodField(read_only=True)

    def get_status_display(self, obj):
        return obj.get_status_display()

    def to_representation(self, instance):
        rep = super(CompareListSerializer, self).to_representation(instance)
        rep['registered_at'] = (instance.registered_at + relativedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")
        return rep


class CompareRepresentationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compare
        fields = [
            'id', 'registered_at', 'serial',
            'account', 'manager', 'customer',
            'attach_1', 'attach_2', 'attach_3', 'driver_range', 'driver_range_display', 'memo',
            'estimate_set', 'contractrequest_set'
        ]

    account = AccountSerializer()
    manager = ManagerSerializer()
    customer = CustomerInfoSerializer()
    driver_range_display = serializers.SerializerMethodField()
    estimate_set = EstimateRepresentationSerializer(many=True)
    contractrequest_set = ContractRequestRepresentationSerializer(many=True)

    def get_driver_range_display(self, obj):
        return obj.get_driver_range_display()

    def to_representation(self, instance):
        rep = super(CompareRepresentationSerializer, self).to_representation(instance)
        rep['registered_at'] = (instance.registered_at + relativedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")
        return rep


class ContractRequestSerializer(serializers.Serializer):
    estimate_detail_id = serializers.IntegerField(required=True, allow_null=False)
    request_msg = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class NoticeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = ['id', 'registered_at', 'updated_at', 'title', 'is_open']

    def to_representation(self, instance):
        rep = super(NoticeListSerializer, self).to_representation(instance)
        rep['registered_at'] = (instance.registered_at + relativedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")
        rep['updated_at'] = (instance.updated_at + relativedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")
        return rep


class NoticeDetailSerializer(NoticeListSerializer):
    class Meta:
        model = Notice
        fields = ['registered_at', 'updated_at', 'title', 'is_open', 'body']

