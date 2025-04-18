import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuard } from './guards/auth.guard';

import { LoginComponent } from './components/auth/login/login.component';
import { RegisterComponent } from './components/auth/register/register.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { ClientListComponent } from './components/clients/client-list/client-list.component';
import { ClientFormComponent } from './components/clients/client-form/client-form.component';
import { QuotationListComponent } from './components/quotations/quotation-list/quotation-list.component';
import { QuotationFormComponent } from './components/quotations/quotation-form/quotation-form.component';
import { InvoiceListComponent } from './components/invoices/invoice-list/invoice-list.component';
import { InvoiceFormComponent } from './components/invoices/invoice-form/invoice-form.component';
import { ExportComponent } from './components/exports/export/export.component';

const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  {
    path: '',
    canActivate: [AuthGuard],
    children: [
      { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
      { path: 'dashboard', component: DashboardComponent },
      { path: 'clients', component: ClientListComponent },
      { path: 'clients/new', component: ClientFormComponent },
      { path: 'clients/:id/edit', component: ClientFormComponent },
      { path: 'quotations', component: QuotationListComponent },
      { path: 'quotations/new', component: QuotationFormComponent },
      { path: 'quotations/:id/edit', component: QuotationFormComponent },
      { path: 'invoices', component: InvoiceListComponent },
      { path: 'invoices/new', component: InvoiceFormComponent },
      { path: 'invoices/:id/edit', component: InvoiceFormComponent },
      { path: 'exports', component: ExportComponent }
    ]
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }