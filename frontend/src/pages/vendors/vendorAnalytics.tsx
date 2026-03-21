import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer
} from "recharts";
import type { NameType, ValueType, Payload } from "recharts/types/component/DefaultTooltipContent";
import type { Vendor } from "../../types";
import { getVendorProfile} from '../../api/vendors';
import { getVendorAnalytics } from "../../api/analytics";

export default function VendorForecasts() {
    return (
        <div>
            Hi
        </div>
    )
}