from django.contrib import admin
from .models import Conversation, ConversationMessage
import json
from django.contrib import messages

# create Product import lazily to avoid import-time DB hits when admin modules are loaded
def _create_product_from_recipe(recipe):
    from products.models import Product
    name = recipe.get('name') if isinstance(recipe, dict) else None
    if not name:
        name = 'Produit personnalisé'
    # collect tags from notes
    tags = []
    for k in ('top_notes', 'heart_notes', 'base_notes'):
        vals = recipe.get(k) if isinstance(recipe, dict) else None
        if isinstance(vals, (list, tuple)):
            tags.extend([str(v) for v in vals if v])

    description_parts = []
    if isinstance(recipe, dict):
        comments = recipe.get('comments')
        if comments:
            description_parts.append(str(comments))
    description = '\n'.join(description_parts)

    prod = Product.objects.create(
        name=name,
        description=description or '',
        price=0.0,
        stock=0,
        family='',
        concentration='',
        image_url='',
        tags=list(set(tags)),
    )
    return prod


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at')
    readonly_fields = ('created_at',)
    search_fields = ('user__username',)
    actions = ['create_product_from_conversation']

    def view_suggested(self, obj):
        return json.dumps(obj.suggested_recipe or {}, indent=2)

    def create_product_from_conversation(self, request, queryset):
        created = 0
        for conv in queryset:
            recipe = conv.suggested_recipe or {}
            if recipe and isinstance(recipe, dict) and recipe.get('name'):
                try:
                    prod = _create_product_from_recipe(recipe)
                    created += 1
                except Exception as e:
                    self.message_user(request, f'Erreur lors de la création pour conversation {conv.id}: {e}', level=messages.ERROR)
            else:
                # skip conversations without recipe
                continue

        if created:
            self.message_user(request, f'Créé {created} produit(s) à partir des conversations sélectionnées.')
        else:
            self.message_user(request, 'Aucune recette valide trouvée dans les conversations sélectionnées.', level=messages.WARNING)


@admin.register(ConversationMessage)
class ConversationMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'role', 'created_at')
    list_filter = ('role',)
    search_fields = ('text',)
