# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.views.decorators.http import require_GET
from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.forms.models import inlineformset_factory
from django.contrib.auth.decorators import login_required, permission_required
from recipes.models import Recipe, Ingredient, RecipeStep, Favorite
from recipes.forms import IngredientForm, RecipeForm, RecipeStepForm


@login_required
def home(request, items_per_page=25):
    recipe_list = Recipe.objects.all()
    page = request.GET.get('page')
    recipes = build_paginator(recipe_list, page, items_per_page)

    return render(request, 'list.html', {
        "recipes": recipes,
        "page_name": 'Recipes',
    })


@login_required
def my_recipes(request, items_per_page=25):
    recipe_list = Recipe.objects.filter(added_by=request.user)
    for r in recipe_list:
        if r.is_user_favorite(request.user):
            r.is_favorite = True
        else:
            r.is_favorite = False
    page = request.GET.get('page')
    recipes = build_paginator(recipe_list, page, items_per_page)

    return render(request, 'list.html', {
        "recipes": recipes,
        "page_name": 'My Recipes',
    })


@login_required
def my_favorites(request, items_per_page=25):
    favorites = Favorite.objects.filter(user=request.user)
    recipe_list = [f.recipe for f in favorites]
    page = request.GET.get('page')
    recipes = build_paginator(recipe_list, page, items_per_page)

    return render(request, 'list.html', {
        "recipes": recipes,
        "page_name": 'Favorites',
    })


@login_required
@permission_required('recipes.add_recipe')
def add(request):
    IngredientFormSet = inlineformset_factory(Recipe, Ingredient, extra=1,
                                              form=IngredientForm)
    RecipeStepFormSet = inlineformset_factory(Recipe, RecipeStep, extra=1,
                                              form=RecipeStepForm)
    if request.method == 'POST':
        recipe_form = RecipeForm(request.POST, request.FILES,
                                 prefix='recipe')
        ingredient_formset = IngredientFormSet(request.POST,
                                               prefix='ingredients')
        recipe_step_formset = RecipeStepFormSet(request.POST,
                                                prefix='recipe_steps')
        if recipe_form.is_valid() and ingredient_formset.is_valid() \
                and recipe_step_formset.is_valid():
            recipe_id = recipe_form.save(commit=False)
            recipe_id.added_by = request.user
            recipe_id.save()
            ingredients = ingredient_formset.save(commit=False)
            for ingredient in ingredients:
                ingredient.recipe = recipe_id
                ingredient.save()
            recipe_steps = recipe_step_formset.save(commit=False)
            for recipe_step in recipe_steps:
                recipe_step.recipe = recipe_id
                recipe_step.save()
            return HttpResponseRedirect(reverse('home'))
    else:
        recipe_form = RecipeForm(prefix='recipe')
        ingredient_formset = IngredientFormSet(prefix='ingredients')
        recipe_step_formset = RecipeStepFormSet(prefix='recipe_steps')

    return render(request, 'add.html', {
        'form_action': reverse('recipe-new'),
        'recipe_form': recipe_form,
        'ingredient_formset': ingredient_formset,
        'recipe_step_formset': recipe_step_formset,
    })


@login_required
@permission_required('recipes.change_recipe')
def update(request, recipe):
    IngredientFormSet = inlineformset_factory(Recipe, Ingredient, extra=0,
                                              form=IngredientForm)
    RecipeStepFormSet = inlineformset_factory(Recipe, RecipeStep, extra=0,
                                              form=RecipeStepForm)
    recipe = get_object_or_404(Recipe, pk=recipe)
    if request.method == 'POST':
        recipe_form = RecipeForm(request.POST, request.FILES,
                                 prefix='recipe', instance=recipe)
        ingredient_formset = IngredientFormSet(request.POST,
                                               prefix='ingredients', instance=recipe)
        recipe_step_formset = RecipeStepFormSet(request.POST,
                                                prefix='recipe_steps', instance=recipe)
        if recipe_form.is_valid() and ingredient_formset.is_valid() and \
                recipe_step_formset.is_valid():
            recipe_form.save()
            ingredient_formset.save()
            recipe_step_formset.save()
            return HttpResponseRedirect(reverse('home'))
    else:
        recipe_form = RecipeForm(instance=recipe, prefix='recipe')
        ingredient_formset = IngredientFormSet(instance=recipe,
                                               prefix='ingredients')
        recipe_step_formset = RecipeStepFormSet(instance=recipe,
                                                prefix='recipe_steps')
    return render(request, 'add.html', {
        'form_action': reverse('recipe-update', args=[recipe.id]),
        'recipe_form': recipe_form,
        'ingredient_formset': ingredient_formset,
        'recipe_step_formset': recipe_step_formset,
    })


@login_required
@require_GET
@permission_required('recipes.delete_recipe')
def remove(request):
    if request.is_ajax() and 'recipe' in request.GET:
        try:
            del_recipe = Recipe.objects.get(pk=request.GET['recipe'])
        except Recipe.DoesNotExist:
            return HttpResponse("Error", content_type="text/plain")
        del_recipe.delete()
        return HttpResponse("Success", content_type="text/plain")
    else:
        return HttpResponseRedirect(reverse('home'))


@login_required
@require_GET
def favorite(request, recipe):
    if request.is_ajax():
        recipe = get_object_or_404(Recipe, pk=recipe)
        if 'remove' in request.GET and request.GET['remove'] == 'True':
            try:
                Favorite.objects.get(recipe=recipe, user=request.user).delete()
            except Favorite.DoesNotExist:
                return HttpResponse("Error", content_type="text/plain")
            else:
                return HttpResponse("Success", content_type="text/plain")
        else:
            try:
                Favorite.objects.get(recipe=recipe, user=request.user)
            except Favorite.DoesNotExist:
                Favorite.objects.create(user=request.user, recipe=recipe)
                return HttpResponse("Success", content_type="text/plain")
            return HttpResponse("Error", content_type="text/plain")
    else:
        return HttpResponseRedirect(reverse('home'))


@login_required
def new_ingredient_form(request):
    if request.is_ajax():
        IngredientFormSet = inlineformset_factory(Recipe, Ingredient, extra=1,
                                                  form=IngredientForm)
        empty_form = IngredientFormSet(prefix='ingredients').empty_form
        return render(request, 'addIngredient.html', {'form': empty_form})
    else:
        return HttpResponseRedirect(reverse('home'))


def new_recipe_step_form(request):
    if request.is_ajax():
        RecipeStepFormSet = inlineformset_factory(Recipe, RecipeStep, extra=1,
                                                  form=RecipeStepForm)
        empty_form = RecipeStepFormSet(prefix='recipe_steps').empty_form
        return render(request, 'addRecipeStep.html', {'form': empty_form})
    else:
        return HttpResponseRedirect(reverse('home'))


@login_required
def get(request, recipe_id):
    try:
        recipe = Recipe.objects.select_related().get(pk=recipe_id)
    except Recipe.DoesNotExist:
        raise Http404
    ingredients = recipe.ingredient_set.all()
    ingredients = ingredients.order_by('number')
    steps = recipe.recipestep_set.all()
    steps = steps.order_by('number')
    return render(request, 'detail.html', {
        "recipe": recipe,
        "ingredients": ingredients,
        "steps": steps,
    })


def build_paginator(query_set, page, items_per_page):
    paginator = Paginator(query_set, items_per_page)
    try:
        ret_paginator = paginator.page(page)
    except PageNotAnInteger:

        ret_paginator = paginator.page(1)
    except EmptyPage:

        ret_paginator = paginator.page(paginator.num_pages)
    return ret_paginator