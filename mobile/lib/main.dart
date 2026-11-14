import 'package:flutter/material.dart';

/// LedgerLens entry point.
///
/// UI-only scaffold: a single screen listing expenses with a scan-receipt
/// action. The scan button appends a locally mocked entry so the screen is
/// fully navigable without a backend. Wire [_onScanPressed] to the camera and
/// `POST /api/receipts/scan` when you integrate the real OCR flow.
void main() => runApp(const LedgerLensApp());

class LedgerLensApp extends StatelessWidget {
  const LedgerLensApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'LedgerLens',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF34D399)),
        useMaterial3: true,
      ),
      home: const ExpensesScreen(),
    );
  }
}

class Expense {
  Expense({required this.merchant, required this.amount, required this.category});

  final String merchant;
  final double amount;
  final String category;
}

class ExpensesScreen extends StatefulWidget {
  const ExpensesScreen({super.key});

  @override
  State<ExpensesScreen> createState() => _ExpensesScreenState();
}

class _ExpensesScreenState extends State<ExpensesScreen> {
  final List<Expense> _expenses = <Expense>[
    Expense(merchant: 'Whole Foods', amount: 48.20, category: 'groceries'),
    Expense(merchant: 'Netflix', amount: 9.99, category: 'subscription'),
  ];

  double get _total => _expenses.fold(0, (sum, e) => sum + e.amount);

  void _onScanPressed() {
    setState(() {
      _expenses.add(
        Expense(merchant: 'Starbucks (scanned)', amount: 12.50, category: 'dining'),
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('LedgerLens'),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16),
            child: Center(child: Text('Total: \$${_total.toStringAsFixed(2)}')),
          ),
        ],
      ),
      body: _expenses.isEmpty
          ? const Center(child: Text('No expenses yet. Scan a receipt to start.'))
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _expenses.length,
              itemBuilder: (context, index) {
                final expense = _expenses[index];
                return Card(
                  child: ListTile(
                    leading: const Icon(Icons.receipt_long),
                    title: Text(expense.merchant),
                    subtitle: Text(expense.category),
                    trailing: Text('\$${expense.amount.toStringAsFixed(2)}'),
                  ),
                );
              },
            ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _onScanPressed,
        icon: const Icon(Icons.camera_alt),
        label: const Text('Scan receipt'),
      ),
    );
  }
}
