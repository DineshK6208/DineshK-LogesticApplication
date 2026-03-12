import express from "express";
import { createServer as createViteServer } from "vite";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  // --- MOCK API DATA ---
  let requests: any[] = [
    {
      id: 1,
      request_number: "REQ-1001",
      status: "pending_payment",
      total_amount: 1250.50,
      notes: "Fragile items, handle with care.",
      items: [
        { id: 101, name: "Mechanical Keyboard", description: "RGB Backlit", quantity: 1, unit_price: 150.50 },
        { id: 102, name: "Curved Monitor", description: "34-inch 4K", quantity: 1, unit_price: 1100.00 }
      ],
      receiver: {
        receiver_name: "John Doe",
        contact_number: "+1 234 567 890",
        delivery_address: "123 Tech Lane",
        city: "San Francisco",
        state: "CA",
        postal_code: "94105"
      },
      created_at: new Date().toISOString()
    }
  ];

  let config = { max_delivery_attempts: 3 };
  let attempts = [];

  // --- API ROUTES ---
  app.get("/api/item-requests", (req, res) => {
    res.json(requests);
  });

  app.get("/api/item-requests/:id", (req, res) => {
    const request = requests.find(r => r.id === parseInt(req.params.id));
    if (request) res.json(request);
    else res.status(404).json({ error: "Not found" });
  });

  app.post("/api/item-requests", (req, res) => {
    const newRequest = {
      ...req.body,
      id: requests.length + 1,
      request_number: `REQ-${1000 + requests.length + 1}`,
      status: "pending_payment",
      total_amount: req.body.items.reduce((acc, i) => acc + (i.quantity * i.unit_price), 0),
      created_at: new Date().toISOString()
    };
    requests.push(newRequest);
    res.status(201).json(newRequest);
  });

  app.post("/api/item-requests/:id/pay", (req, res) => {
    const request = requests.find(r => r.id === parseInt(req.params.id));
    if (request) {
      request.status = "paid";
      request.payment = {
        id: Math.floor(Math.random() * 1000),
        payment_method: req.body.payment_method,
        transaction_id: req.body.transaction_id,
        amount: request.total_amount,
        status: "success",
        created_at: new Date().toISOString()
      };
      res.json(request);
    } else res.status(404).json({ error: "Not found" });
  });

  app.patch("/api/item-requests/:id/tracking", (req, res) => {
    const request = requests.find(r => r.id === parseInt(req.params.id));
    if (request) {
      request.tracking = {
        ...request.tracking,
        ...req.body,
        last_updated: new Date().toISOString()
      };
      if (req.body.status === 'delivered') request.status = 'delivered';
      else if (req.body.status === 'in_transit') request.status = 'in_delivery';
      res.json(request.tracking);
    } else res.status(404).json({ error: "Not found" });
  });

  app.post("/api/attempts", (req, res) => {
    const attempt = {
      ...req.body,
      id: attempts.length + 1,
      created_at: new Date().toISOString()
    };
    attempts.push(attempt);
    res.status(201).json(attempt);
  });

  app.patch("/api/attempts/:id/upload-proof", (req, res) => {
    res.json({ status: "success" });
  });

  app.get("/api/delivery-config", (req, res) => {
    res.json(config);
  });

  app.put("/api/delivery-config", (req, res) => {
    config = req.body;
    res.json(config);
  });

  // --- VITE MIDDLEWARE ---
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
