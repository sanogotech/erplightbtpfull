import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { AuthInterceptor } from './interceptors/auth.interceptor';

// Layout components
import { HeaderComponent } from './components/layout/header/header.component';
import { SidebarComponent } from './components/layout/sidebar/sidebar.component';

// Auth components
import { LoginComponent } from './components/auth/login/login.component';
import { RegisterComponent } from './components/auth/register/register.component';

// Feature components
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { ClientListComponent } from './components/clients/client-list/client-list.component';
import { ClientFormComponent } from './components/clients/client-form/client-form.component';
import { QuotationListComponent } from './components/quotations/quotation-list/quotation-list.component';
import { QuotationFormComponent } from './components/quotations/quotation-form/quotation-form.component';
import { InvoiceListComponent } from './components/invoices/invoice-list/invoice-list.component';
import { InvoiceFormComponent } from './components/invoices/invoice-form/invoice-form.component';
import { ExportComponent } from './components/exports/export/export.component';

@NgModule({
  declarations: [
    AppComponent,
    HeaderComponent,
    SidebarComponent,
    LoginComponent,
    RegisterComponent,
    DashboardComponent,
    ClientListComponent,
    ClientFormComponent,
    QuotationListComponent,
    QuotationFormComponent,
    InvoiceListComponent,
    InvoiceFormComponent,
    ExportComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    ReactiveFormsModule,
    NgbModule
  ],
  providers: [
    { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }