import graphene
from graphene_django.types import DjangoObjectType
from .models import Category, Ingredient

# Define GraphQL types for Category and Ingredient models using DjangoObjectType
class CategoryType(DjangoObjectType):
    class Meta:
        model = Category

class IngredientType(DjangoObjectType):
    class Meta:
        model = Ingredient

# Define the Query type with fields to retrieve all categories and ingredients
class Query(graphene.ObjectType):
    all_categories = graphene.List(CategoryType)
    all_ingredients = graphene.List(IngredientType)

    category_by_id = graphene.Field(CategoryType, id=graphene.ID())
    ingredient_by_id = graphene.Field(IngredientType, id=graphene.ID())

    # Resolver functions for retrieving all categories and ingredients
    def resolve_all_categories(self, info):
        return Category.objects.all()
    
    def resolve_all_ingredients(self, info):
        return Ingredient.objects.all()
    
    def resolve_category_by_id(self, info, id):
        try:
            return Category.objects.get(pk=id)
        except Category.DoesNotExist:
            return None
        
    def resolve_ingredient_by_id(self, info, id):
        try:
            return Ingredient.objects.get(pk=id)
        except Ingredient.DoesNotExist:
            return None

# Define mutations for creating, updating, and deleting categories and ingredients
class CreateCategory(graphene.Mutation):
    class Arguments:
        name = graphene.String()
    
    category = graphene.Field(CategoryType)
    
    def mutate(self, info, name):
        # Create a new Category instance and save it
        category = Category(name=name)
        category.save()
        return CreateCategory(category=category)
    

class CreateIngredient(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        category_id = graphene.Int()

    ingredient = graphene.Field(IngredientType)

    def mutate(self, info, name, category_id):
        # Retrieve the associated Category instance and create a new Ingredient
        category = Category.objects.get(pk=category_id)
        ingredient = Ingredient(name=name, category=category)
        ingredient.save()
        return CreateIngredient(ingredient=ingredient)
    

class CreateIngredientByCategoryName(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        category_name = graphene.String()

    ingredient = graphene.Field(IngredientType)

    def mutate(self, info, name, category_name):
        try:
            category = Category.objects.get(name=category_name)
        except Category.DoesNotExist:
            raise Exception(f"Category with name '{category_name}' not found.")

        ingredient = Ingredient(name=name, category=category)
        ingredient.save()
        return CreateIngredientByCategoryName(ingredient=ingredient)

class UpdateCategory(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        name = graphene.String()
    
    category = graphene.Field(CategoryType)
    
    def mutate(self, info, id, name):
        try:
            # Retrieve the existing Category, update its name, and save
            category = Category.objects.get(pk=id)
            category.name = name
            category.save()
            return UpdateCategory(category=category)
        except Category.DoesNotExist:
            raise Exception(f"Category with ID {id} not found.")

class UpdateIngredient(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        name = graphene.String()
        category_id = graphene.Int()

    ingredient = graphene.Field(IngredientType)

    def mutate(self, info, id, name=None, category_id=None):
        try:
            # Retrieve the existing Ingredient, update its name and/or category, and save
            ingredient = Ingredient.objects.get(pk=id)
        except Ingredient.DoesNotExist:
            raise Exception(f"Ingredient with ID {id} not found.")
        
        if name is not None:
            ingredient.name = name
        if category_id is not None:
            category = Category.objects.get(pk=category_id)
            ingredient.category = category
        
        ingredient.save()

        return UpdateIngredient(ingredient=ingredient)

class DeleteCategory(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
    
    success = graphene.Boolean()
    
    def mutate(self, info, id):
        # Retrieve the Category instance, delete it, and return success
        category = Category.objects.get(pk=id)
        category.delete()
        return DeleteCategory(success=True)

class DeleteIngredient(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, id):
        try:
            # Retrieve the Ingredient instance, delete it, and return success with a message
            ingredient = Ingredient.objects.get(pk=id)
            ingredient.delete()
            return DeleteIngredient(success=True, message=f"Ingredient with ID {id} deleted.")
        except Ingredient.DoesNotExist:
            return DeleteIngredient(success=False, message=f"Ingredient with ID {id} not found.")

# Define the Mutation type with fields for all defined mutations
class Mutation(graphene.ObjectType):
    create_category = CreateCategory.Field()
    create_ingredient = CreateIngredient.Field()
    create_ingredient_by_category_name = CreateIngredientByCategoryName.Field()
    update_category = UpdateCategory.Field()
    update_ingredient = UpdateIngredient.Field()
    delete_category = DeleteCategory.Field()
    delete_ingredient = DeleteIngredient.Field()


# Define the schema with the Query and Mutation types
schema = graphene.Schema(query=Query, mutation=Mutation)
