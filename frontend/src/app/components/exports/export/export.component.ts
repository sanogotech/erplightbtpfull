import { Component, OnInit } from '@angular/core';
import { ExportService } from '../../../services/export.service';
import { ToastService } from '../../../services/toast.service';

@Component({
  selector: 'app-export',
  template: `
    <div class="container-fluid">
      <h2 class="mb-4">JD Edwards Exports</h2>
      
      <!-- Pending Exports Section -->
      <div class="card mb-4">
        <div class="card-header">
          <h5 class="card-title mb-0">Pending Exports</h5>
        </div>
        <div class="card-body">
          <!-- Invoices -->
          <h6>Invoices</h6>
          <div class="table-responsive mb-4">
            <table class="table table-striped">
              <thead>
                <tr>
                  <th><input type="checkbox" (change)="toggleAllInvoices($event)"></th>
                  <th>Reference</th>
                  <th>Client</th>
                  <th>Amount</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                <tr *ngFor="let invoice of pendingExports.invoices">
                  <td><input type="checkbox" [(ngModel)]="invoice.selected"></td>
                  <td>{{ invoice.reference }}</td>
                  <td>{{ invoice.client_name }}</td>
                  <td>{{ invoice.total_amount | currency:'EUR' }}</td>
                  <td>{{ invoice.created_at | date:'short' }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Payments -->
          <h6>Payments</h6>
          <div class="table-responsive mb-4">
            <table class="table table-striped">
              <thead>
                <tr>
                  <th><input type="checkbox" (change)="toggleAllPayments($event)"></th>
                  <th>Reference</th>
                  <th>Invoice</th>
                  <th>Amount</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                <tr *ngFor="let payment of pendingExports.payments">
                  <td><input type="checkbox" [(ngModel)]="payment.selected"></td>
                  <td>{{ payment.reference }}</td>
                  <td>{{ payment.invoice_reference }}</td>
                  <td>{{ payment.amount | currency:'EUR' }}</td>
                  <td>{{ payment.payment_date | date:'short' }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Export Actions -->
          <div class="d-flex gap-2">
            <button class="btn btn-primary" (click)="exportSelected('invoice')" [disabled]="!hasSelectedInvoices()">
              Export Selected Invoices
            </button>
            <button class="btn btn-primary" (click)="exportSelected('payment')" [disabled]="!hasSelectedPayments()">
              Export Selected Payments
            </button>
          </div>
        </div>
      </div>

      <!-- Export History Section -->
      <div class="card">
        <div class="card-header">
          <h5 class="card-title mb-0">Export History</h5>
        </div>
        <div class="card-body">
          <div class="table-responsive">
            <table class="table table-striped">
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Date</th>
                  <th>Records</th>
                  <th>Error</th>
                </tr>
              </thead>
              <tbody>
                <tr *ngFor="let export of exportHistory">
                  <td>{{ export.type }}</td>
                  <td>
                    <span [class]="'badge ' + getStatusBadgeClass(export.status)">
                      {{ export.status }}
                    </span>
                  </td>
                  <td>{{ export.export_date | date:'short' }}</td>
                  <td>{{ export.record_id }}</td>
                  <td>{{ export.error_message }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  `
})
export class ExportComponent implements OnInit {
  pendingExports: any = { invoices: [], payments: [] };
  exportHistory: any[] = [];

  constructor(
    private exportService: ExportService,
    private toastService: ToastService
  ) {}

  ngOnInit(): void {
    this.loadPendingExports();
    this.loadExportHistory();
  }

  loadPendingExports(): void {
    this.exportService.getPendingExports().subscribe({
      next: (data) => {
        this.pendingExports = data;
        // Add selected property to each item
        this.pendingExports.invoices.forEach((inv: any) => inv.selected = false);
        this.pendingExports.payments.forEach((pay: any) => pay.selected = false);
      },
      error: (error) => {
        this.toastService.show('Error loading pending exports', 'error');
      }
    });
  }

  loadExportHistory(): void {
    this.exportService.getExportHistory().subscribe({
      next: (data) => {
        this.exportHistory = data;
      },
      error: (error) => {
        this.toastService.show('Error loading export history', 'error');
      }
    });
  }

  toggleAllInvoices(event: any): void {
    const checked = event.target.checked;
    this.pendingExports.invoices.forEach((inv: any) => inv.selected = checked);
  }

  toggleAllPayments(event: any): void {
    const checked = event.target.checked;
    this.pendingExports.payments.forEach((pay: any) => pay.selected = checked);
  }

  hasSelectedInvoices(): boolean {
    return this.pendingExports.invoices.some((inv: any) => inv.selected);
  }

  hasSelectedPayments(): boolean {
    return this.pendingExports.payments.some((pay: any) => pay.selected);
  }

  exportSelected(type: 'invoice' | 'payment'): void {
    const items = type === 'invoice' ? this.pendingExports.invoices : this.pendingExports.payments;
    const selectedIds = items
      .filter((item: any) => item.selected)
      .map((item: any) => item.id);

    if (selectedIds.length === 0) {
      this.toastService.show('Please select items to export', 'warning');
      return;
    }

    this.exportService.generateExport(type, selectedIds).subscribe({
      next: (response) => {
        this.toastService.show(`Successfully exported ${response.record_count} ${type}(s)`, 'success');
        this.loadPendingExports();
        this.loadExportHistory();
      },
      error: (error) => {
        this.toastService.show(`Error exporting ${type}s: ${error.error?.message || 'Unknown error'}`, 'error');
      }
    });
  }

  getStatusBadgeClass(status: string): string {
    switch (status) {
      case 'success': return 'bg-success';
      case 'failed': return 'bg-danger';
      case 'pending': return 'bg-warning';
      default: return 'bg-secondary';
    }
  }
}