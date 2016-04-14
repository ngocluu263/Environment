from django import forms
from django.template.loader import render_to_string

class SelectWithPopUp(forms.Select):
    #template = 'ecalc/_newpopup.html'
    def __init__(self, model=None, template='ecalc/_newpopup.html', *args, **kwargs):
        self.model = model
        self.template = template
        super(SelectWithPopUp, self).__init__(*args, **kwargs)
    def render(self, name, *args, **kwargs):
        html = super(SelectWithPopUp, self).render(name, *args, **kwargs)
        popupplus = render_to_string(self.template, {'field': name, 'model': self.model, 'url': self.url})
        return html+popupplus

#class FilteredMultipleSelectWithPopUp(PopUpBaseWidget, FilteredSelectMultiple):
#    pass

#class MultipleSelectWithPopUp(PopUpBaseWidget, forms.SelectMultiple):
#    pass

#class SelectWithPopUp(PopUpBaseWidget, forms.Select):
#    pass
