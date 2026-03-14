"use client";

import { useEffect, useState } from "react";
import {
  Badge,
  Card,
  Grid,
  Metric,
  ProgressBar,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeaderCell,
  TableRow,
  Text,
  Title,
} from "@tremor/react";
import { AlertTriangle, PackageCheck, TrendingDown } from "lucide-react";

type InventoryItem = {
  stock_code: string;
  description: string;
  current_stock_level: number;
  dead_stock_probability: number;
  suggested_discount: number;
};

type InventoryResponse = {
  items: InventoryItem[];
  total_items: number;
  dead_stock_count: number;
};

const emptyInventoryData: InventoryResponse = {
  items: [],
  total_items: 0,
  dead_stock_count: 0,
};

export default function Dashboard() {
  const [data, setData] = useState<InventoryResponse>(emptyInventoryData);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    let isMounted = true;

    async function loadInventory() {
      try {
        const res = await fetch("http://localhost:8000/inventory/health", {
          cache: "no-store",
        });

        if (!res.ok) {
          throw new Error(`Inventory API returned ${res.status}`);
        }

        const payload = (await res.json()) as InventoryResponse;

        if (!isMounted) {
          return;
        }

        setData(payload);
        setErrorMessage("");
      } catch (err) {
        if (!isMounted) {
          return;
        }

        console.error("FastAPI not running?", err);
        setData(emptyInventoryData);
        setErrorMessage("Backend unavailable. Start the FastAPI server on port 8000.");
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    loadInventory();

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <main className="min-h-screen bg-slate-50 p-8">
      <div className="mx-auto max-w-7xl">
        <header className="mb-10">
          <Title className="text-4xl font-extrabold text-slate-900">
            Inventory Health AI
          </Title>
          <Text className="text-lg text-slate-500">
            Scikit-learn powered predictive forecasting and margin optimization.
          </Text>
        </header>

        {errorMessage ? (
          <Card className="mb-8 border border-rose-200 bg-rose-50">
            <Text className="text-rose-700">{errorMessage}</Text>
          </Card>
        ) : null}

        <Grid numItemsLg={3} className="mb-8 gap-6">
          <Card decoration="top" decorationColor="blue">
            <div className="flex items-center space-x-4">
              <PackageCheck className="text-blue-500" size={32} />
              <div>
                <Text>Active Inventory SKUs</Text>
                <Metric>{data.total_items}</Metric>
              </div>
            </div>
          </Card>

          <Card decoration="top" decorationColor="red">
            <div className="flex items-center space-x-4">
              <AlertTriangle className="text-red-500" size={32} />
              <div>
                <Text>Dead Stock Identified</Text>
                <Metric>{data.dead_stock_count}</Metric>
              </div>
            </div>
          </Card>

          <Card decoration="top" decorationColor="emerald">
            <div className="flex items-center space-x-4">
              <TrendingDown className="text-emerald-500" size={32} />
              <div>
                <Text>Recovery Potential</Text>
                <Metric>$ {(data.dead_stock_count * 125).toLocaleString()}</Metric>
              </div>
            </div>
          </Card>
        </Grid>

        <Card className="mt-8">
          <div className="mb-6 flex items-center justify-between">
            <Title>AI Analysis: Dead Stock Risk and Prescriptive Discounts</Title>
            <Badge color="rose" icon={AlertTriangle}>
              {isLoading ? "Loading" : "Requires Action"}
            </Badge>
          </div>

          <Table>
            <TableHead>
              <TableRow>
                <TableHeaderCell>Product Description</TableHeaderCell>
                <TableHeaderCell>Stock Level</TableHeaderCell>
                <TableHeaderCell>Dead Stock Probability</TableHeaderCell>
                <TableHeaderCell>Risk Level</TableHeaderCell>
                <TableHeaderCell>Suggested Discount</TableHeaderCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {data.items.map((item) => (
                <TableRow key={item.stock_code}>
                  <TableCell>
                    <Text className="font-bold text-slate-800">
                      {item.description}
                    </Text>
                    <span className="font-mono text-xs text-slate-400">
                      SKU: {item.stock_code}
                    </span>
                  </TableCell>
                  <TableCell>{item.current_stock_level}</TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-3">
                      <ProgressBar
                        className="w-32"
                        color={item.dead_stock_probability > 0.8 ? "rose" : "amber"}
                        value={item.dead_stock_probability * 100}
                      />
                      <span className="text-sm font-medium">
                        {(item.dead_stock_probability * 100).toFixed(0)}%
                      </span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge color={item.dead_stock_probability > 0.8 ? "rose" : "orange"}>
                      {item.dead_stock_probability > 0.8 ? "CRITICAL" : "AT RISK"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <span className="text-lg font-bold text-emerald-600">
                      -{item.suggested_discount}%
                    </span>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          {!isLoading && data.items.length === 0 ? (
            <Text className="mt-6 text-slate-500">
              No flagged inventory records are available.
            </Text>
          ) : null}
        </Card>
      </div>
    </main>
  );
}
