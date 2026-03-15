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
import {
  AlertTriangle,
  ArrowDownRight,
  Boxes,
  CircleDollarSign,
  Sparkles,
} from "lucide-react";

type InventoryItem = {
  stock_code: string;
  description: string | null;
  category: string | null;
  unit_price: number;
  current_stock_level: number;
  last_sold_date: string | null;
  days_since_last_sale: number | null;
  dead_stock_probability: number;
  is_dead_stock: boolean;
  suggested_discount: number;
  inventory_value: number;
};

type InventoryResponse = {
  items: InventoryItem[];
  total_items: number;
  dead_stock_count: number;
  at_risk_revenue: number;
  generated_at: string;
};

const emptyInventoryData: InventoryResponse = {
  items: [],
  total_items: 0,
  dead_stock_count: 0,
  at_risk_revenue: 0,
  generated_at: "",
};

const apiBaseUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

function formatCurrency(value: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

function formatRiskLabel(probability: number) {
  if (probability > 0.8) {
    return { label: "Critical", color: "rose" as const };
  }
  if (probability >= 0.5) {
    return { label: "At Risk", color: "amber" as const };
  }
  return { label: "Watch", color: "emerald" as const };
}

export default function Dashboard() {
  const [data, setData] = useState<InventoryResponse>(emptyInventoryData);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    let isMounted = true;

    async function loadInventory() {
      try {
        const res = await fetch(`${apiBaseUrl}/inventory/health`, {
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
      } catch (error) {
        if (!isMounted) {
          return;
        }

        console.error(error);
        setData(emptyInventoryData);
        setErrorMessage("Backend unavailable. Start FastAPI on port 8000 or set NEXT_PUBLIC_API_BASE_URL.");
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

  const generatedAtLabel = data.generated_at
    ? new Date(data.generated_at).toLocaleString()
    : "Pending model run";

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(15,118,110,0.18),_transparent_30%),linear-gradient(180deg,_#f5f5f4_0%,_#ecfccb_100%)] px-4 py-8 text-stone-900 sm:px-6 lg:px-10">
      <div className="mx-auto max-w-7xl">
        <section className="mb-8 overflow-hidden rounded-[2rem] border border-white/60 bg-white/75 p-8 shadow-[0_24px_80px_rgba(41,37,36,0.08)] backdrop-blur">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-3xl">
              <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-teal-950 px-3 py-1 text-xs font-semibold uppercase tracking-[0.24em] text-teal-50">
                <Sparkles size={14} />
                AI-Driven Inventory Health
              </div>
              <Title className="font-serif text-4xl text-stone-900 sm:text-5xl">
                Dead-stock detection with recovery recommendations
              </Title>
              <Text className="mt-3 max-w-2xl text-base text-stone-600">
                The dashboard flags idle SKUs, scores dead-stock probability, and recommends clearance discounts to recover capital faster.
              </Text>
            </div>

            <Card className="max-w-sm rounded-3xl border-0 bg-stone-950 text-stone-50 shadow-none">
              <Text className="text-stone-300">Last model refresh</Text>
              <Metric className="mt-2 text-2xl">{generatedAtLabel}</Metric>
            </Card>
          </div>
        </section>

        {errorMessage ? (
          <Card className="mb-8 rounded-3xl border border-rose-200 bg-rose-50">
            <Text className="text-rose-700">{errorMessage}</Text>
          </Card>
        ) : null}

        <Grid numItems={1} numItemsMd={2} numItemsLg={3} className="gap-6">
          <Card className="rounded-3xl border-0 bg-white/85 shadow-[0_12px_40px_rgba(41,37,36,0.08)]">
            <div className="flex items-start justify-between">
              <div>
                <Text>Total Items</Text>
                <Metric className="mt-3">{data.total_items.toLocaleString()}</Metric>
              </div>
              <div className="rounded-2xl bg-stone-100 p-3 text-stone-700">
                <Boxes size={24} />
              </div>
            </div>
          </Card>

          <Card className="rounded-3xl border-0 bg-white/85 shadow-[0_12px_40px_rgba(41,37,36,0.08)]">
            <div className="flex items-start justify-between">
              <div>
                <Text>Dead Stock Count</Text>
                <Metric className="mt-3">{data.dead_stock_count.toLocaleString()}</Metric>
              </div>
              <div className="rounded-2xl bg-rose-100 p-3 text-rose-600">
                <AlertTriangle size={24} />
              </div>
            </div>
          </Card>

          <Card className="rounded-3xl border-0 bg-white/85 shadow-[0_12px_40px_rgba(41,37,36,0.08)]">
            <div className="flex items-start justify-between">
              <div>
                <Text>At-Risk Revenue</Text>
                <Metric className="mt-3">{formatCurrency(data.at_risk_revenue)}</Metric>
              </div>
              <div className="rounded-2xl bg-emerald-100 p-3 text-emerald-600">
                <CircleDollarSign size={24} />
              </div>
            </div>
          </Card>
        </Grid>

        <Card className="mt-8 rounded-[2rem] border-0 bg-white/85 shadow-[0_12px_40px_rgba(41,37,36,0.08)]">
          <div className="mb-6 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <Title className="font-serif text-2xl text-stone-900">
                Highest-risk inventory
              </Title>
              <Text className="mt-1 text-stone-600">
                Top 15 items ranked by dead-stock probability from the latest model run.
              </Text>
            </div>
            <Badge
              color={data.dead_stock_count > 0 ? "rose" : "emerald"}
              icon={ArrowDownRight}
            >
              {isLoading ? "Loading" : `${data.dead_stock_count} flagged`}
            </Badge>
          </div>

          <Table>
            <TableHead>
              <TableRow>
                <TableHeaderCell>Product</TableHeaderCell>
                <TableHeaderCell>Category</TableHeaderCell>
                <TableHeaderCell>Stock Level</TableHeaderCell>
                <TableHeaderCell>Days Since Sale</TableHeaderCell>
                <TableHeaderCell>Dead Stock Probability</TableHeaderCell>
                <TableHeaderCell>Recommendation</TableHeaderCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {data.items.map((item) => {
                const risk = formatRiskLabel(item.dead_stock_probability);

                return (
                  <TableRow key={item.stock_code}>
                    <TableCell>
                      <div className="space-y-1">
                        <Text className="font-semibold text-stone-900">
                          {item.description || "Unnamed item"}
                        </Text>
                        <Text className="font-mono text-xs text-stone-500">
                          {item.stock_code}
                        </Text>
                      </div>
                    </TableCell>
                    <TableCell>{item.category || "Uncategorized"}</TableCell>
                    <TableCell>{item.current_stock_level.toLocaleString()}</TableCell>
                    <TableCell>{item.days_since_last_sale ?? "N/A"}</TableCell>
                    <TableCell>
                      <div className="flex min-w-44 items-center gap-3">
                        <ProgressBar
                          value={item.dead_stock_probability * 100}
                          color={risk.color}
                          className="w-28"
                        />
                        <div className="space-y-1">
                          <Text className="font-medium text-stone-900">
                            {(item.dead_stock_probability * 100).toFixed(0)}%
                          </Text>
                          <Badge color={risk.color}>{risk.label}</Badge>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      {item.suggested_discount > 0 ? (
                        <Text className="font-semibold text-emerald-700">
                          Mark down {item.suggested_discount}%
                        </Text>
                      ) : (
                        <Text className="text-stone-500">Hold current pricing</Text>
                      )}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>

          {!isLoading && data.items.length === 0 ? (
            <Text className="mt-6 text-stone-500">
              No prediction rows are available yet. Run the seed and prediction scripts first.
            </Text>
          ) : null}
        </Card>
      </div>
    </main>
  );
}
