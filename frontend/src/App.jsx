import CustomerForm from "./components/CustomerForm";
import CustomerTable from "./components/CustomerTable";
import Chatbot from "./components/Chatbot";

export default function App() {
  return (
    <div className="container mx-auto max-w-5xl py-10 space-y-6">
      <header className="text-center space-y-2">
        <h1 className="text-3xl font-bold">Gemini CRUD (ADK Tools) — Full Stack + Voice</h1>
        <p className="text-gray-600">Form + Chatbot (both write to the same DB)</p>
      </header>

      <div className="grid md:grid-cols-2 gap-6">
        <CustomerForm />
        <Chatbot />
      </div>

      <CustomerTable />
    </div>
  );
}
