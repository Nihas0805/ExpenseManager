from django.shortcuts import render,redirect

from django.views.generic import View

from budget.forms import ExpenseForm,RegistrationForm,SignInForm

from django.contrib import messages

from budget.models import Expense

from django import forms

from django.db.models import Q

from django.contrib.auth.models import User

from django.contrib.auth import authenticate,login,logout

from budget.decorators import signin_required

from django.utils.decorators import method_decorator

from django.views.decorators.cache import never_cache

decs=[signin_required,never_cache]

@method_decorator(decs,name="dispatch")
class ExpenseCreateView(View):

    def get(self,request,*args,**kwargs):

        form_instance=ExpenseForm()

        return render(request,"expense_create.html",{"form":form_instance})

    def post(self,request,*args,**kwargs):

        form_instance=ExpenseForm(request.POST)

        if form_instance.is_valid():

            form_instance.instance.user=request.user

            form_instance.save()

            messages.success(request,"Added successfully")

            return redirect("expense-list")

        else:

            messages.error(request,"Add failed")

            return render(request,"expense_create.html",{"form":form_instance})


@method_decorator(decs,name="dispatch")
class ExpenseListView(View):

    def get(self,request,*args,**kwargs):

        search_text=request.GET.get("search_text")

        selected_category=request.GET.get("category","all")

        if search_text != None:

            qs=Expense.objects.filter(user=request.user)

            qs=qs.filter(Q(title__icontains=search_text)|Q(category__icontains=search_text))

        else:

            if selected_category =="all":
                
                qs=Expense.objects.filter(user=request.user)
            
            else:
                
                qs=Expense.objects.filter(category=selected_category,user=request.user)

        return render(request,"expense_list.html",{"expenses":qs,"selected":selected_category})


@method_decorator(decs,name="dispatch")
class ExpenseUpdateView(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        expense_obj=Expense.objects.get(id=id)

        form_instance=ExpenseForm(instance=expense_obj)

        return render(request,"expense_edit.html",{"form":form_instance})


    def post(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        expense_obj=Expense.objects.get(id=id)

        form_instance=ExpenseForm(request.POST,instance=expense_obj)

        if form_instance.is_valid():

            form_instance.save()

            messages.success(request,"Updated Successfully")
            
            return redirect('expense-list')

        else:

            messages.error(request,"Failed to Update")

            return render(request,"expense_edit.html",{"form":form_instance})


@method_decorator(decs,name="dispatch")
class ExpenseDeleteView(View):

        def get(self,request,*args,**kwargs):

            Expense.objects.get(id=kwargs.get("pk")).delete()

            messages.error(request,"Deleted Successfully")

            return redirect("expense-list")



from django.db.models import Count


@method_decorator(decs,name="dispatch")
class ExpenseSummaryView(View):

       template_name="dash_board.html"

       def get(self,request,*args,**kwargs):

        qs=Expense.objects.filter(user=request.user)

        total_task_count=qs.count()

        category_summary=qs.values("category").annotate(cat_count=Count("category"))

        
        context={
            "total_task_count":total_task_count,

            "category_summary":category_summary,
        }

        return render(request,self.template_name,context)


class SignUpView(View):

    template_name="register.html"

    def get(self,request,*args,**kwargs):

        form_instance=RegistrationForm()

        return render(request,self.template_name,{"form":form_instance})

    def post(self,request,*args,**kwargs):

        form_instance=RegistrationForm(request.POST)

        if form_instance.is_valid():

            data=form_instance.cleaned_data

            User.objects.create_user(**data)

            # form_instance.save()

            return redirect("signin")

        else:

            return render(request,self.template_name,{"form":form_instance})


class SignInView(View):

    template_name="login.html"

    def get(self,request,*args,**kwargs):

        form_instance=SignInForm()

        return render(request,self.template_name,{"form":form_instance})

    def post(self,request,*args,**kwargs):

        form_instance=SignInForm(request.POST)

        if form_instance.is_valid():

            #extract username password
            username=form_instance.cleaned_data.get("username")

            password=form_instance.cleaned_data.get("password")

            # authenticate

            user_object=authenticate(request,username=username,password=password)

            if user_object:

                login(request,user_object)

                return redirect("expense-list")

        return render(request,self.template_name,{"form":form_instance})


@method_decorator(decs,name="dispatch")
class SignOutView(View):
    

    def get(self,request,*args,**kwargs):

        logout(request)

        return redirect("signin")


# @method_decorator(decs,name="dispatch")
# class DashBoaardView(View):
    

#     def get(self,request,*args,**kwargs):

#         return render(request,self.template_name)
