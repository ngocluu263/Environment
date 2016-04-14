from tastypie.authorization import Authorization
from tastypie.exceptions import Unauthorized


# adapted from http://django-tastypie.readthedocs.org/en/latest/authorization.html
#
# Usage:
# class ApiResource(ModelResource):
#     class Meta:
#         queryset = model_name.objects.all()
#         authorization = OwnerAuthorization('model_owner_attribute')
#
# TODO: This class is duplicated in mrvapi/v1.py and can be consolidated to one Django application
class OwnerAuthorization(Authorization):
    def __init__(self, filter):
        # This Authorization class receives a string in the constructor
        # This string identifies the object member that should be compared against bundle.request.user
        self.filter = filter
        self.filter_list = filter.split('__')
        self.filter_dict = {filter: None}

    def read_list(self, object_list, bundle):
        # This assumes a ``QuerySet`` from ``ModelResource``.
        self.filter_dict[self.filter] = bundle.request.user
        return object_list.filter(**self.filter_dict)

    def read_detail(self, object_list, bundle):
        # Is the requested object owned by the user?
        owner = bundle.obj
        for filter in self.filter_list:  # works recursively, climbing up FK relations to get owner
            owner = getattr(owner, filter)

        # while this does return False for un-authorized users, and SHOULD work according to documentation -- it does NOT.
        #    return owner == bundle.request.user  # This False is ignored; anyone could see object(s)
        # This comment should remain until upstream issue can be filed/reviewed by tastypie project maintainer
        # We must rather raise an exception:
        if not owner == bundle.request.user:
            raise Unauthorized("You do not have access to this resource.")
        return True

    def create_list(self, object_list, bundle):
        # Assuming they are already assigned to ``user``.
        return object_list

    def create_detail(self, object_list, bundle):
        # 1- get the related owner of the object from a filter like 'parcel__project__owner'
        # owner = bundle.obj
        # for filter in self.filter_list:
        #     owner = getattr(owner, filter)
        # expected result:
        #   owner => bundle.obj.parcel.project.owner
        # actual result:
        #   File "C:\python27\lib\site-packages\django\db\models\fields\related.py", line 387, in __get__
        #   raise self.field.rel.to.DoesNotExist
        #   DoesNotExist
        # 2- compare owner with user request
        # return owner == bundle.request.user

        # cannot get working, will have to authorize all POSTs in interim -- unsecure
        return True

    def update_list(self, object_list, bundle):
        allowed = []

        # Since they may not all be saved, iterate over them.
        for obj in object_list:
            if getattr(obj, self.filter) == bundle.request.user:
                allowed.append(obj)

        return allowed

    def update_detail(self, object_list, bundle):
        # Is the requested object owned by the user?
        owner = bundle.obj
        for filter in self.filter_list:
            owner = getattr(owner, filter)
        if not owner == bundle.request.user:
            raise Unauthorized("You do not have access to this resource.")
        return True

    def delete_list(self, object_list, bundle):
        allowed = []

        for obj in object_list:
            if getattr(obj, self.filter) == bundle.request.user:
                allowed.append(obj)

        return allowed

    def delete_detail(self, object_list, bundle):
        # Is the requested object owned by the user?
        owner = bundle.obj
        for filter in self.filter_list:
            owner = getattr(owner, filter)
        if not owner == bundle.request.user:
            raise Unauthorized("You do not have access to this resource.")
        return True


# adapted from http://django-tastypie.readthedocs.org/en/latest/authorization.html
class OwnerAuthorizationWithPublic(OwnerAuthorization):
    def read_list(self, object_list, bundle):
        # This assumes a ``QuerySet`` from ``ModelResource``.
        self.filter_dict[self.filter] = bundle.request.user
        owners_list = object_list.filter(**self.filter_dict)
        public_list = object_list.filter(public=True)
        return (owners_list | public_list)

    def read_detail(self, object_list, bundle):
        # Is the requested object owned by the user?  or is it public?
        owner = bundle.obj
        for filter in self.filter_list:  # works recursively, climbing up FK relations to get owner
            owner = getattr(owner, filter)
        if (not bundle.obj.public) and (owner != bundle.request.user):
            raise Unauthorized("You do not have access to this resource.")
        return True
