from django.contrib import messages
from django.views.generic.edit import DeleteView

from .permission_mixins import SuperUserCheckMixin


class DeleteViewMixin(SuperUserCheckMixin, DeleteView):
    template_name = "delete.html"
    success_message = "Item was successfully deleted"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteViewMixin, self).delete(request, *args, **kwargs)
        