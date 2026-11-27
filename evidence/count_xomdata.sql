-- ============================================================================
-- Script đếm bằng chứng từ vietnam_ecommerce (Xóm Dataset - SQL Server)
-- Nhóm OLODO · L3A · Track D3
-- QUY TẮC AN TOÀN: Tuyệt đối KHÔNG truy vấn cột PII và KHÔNG lưu mật khẩu.
-- LƯU Ý MẪU SỐ: order_sn / order_id đã bị mask bằng dấu '*', chỉ còn 35 / 386
-- giá trị distinct -> mọi thống kê phải đếm ở cấp dòng hàng (row).
-- ============================================================================

-- 1. Tổng quan khoảng thời gian, số dòng và phân bổ trạng thái
SELECT COUNT(*) AS rows_cnt, COUNT(DISTINCT shop_name) AS shops_cnt,
       MIN(create_time) AS min_dt, MAX(create_time) AS max_dt,
       DATEDIFF(DAY, MIN(create_time), MAX(create_time)) + 1 AS days_span
FROM vietnam_ecommerce.shopee_orders;

SELECT order_status, COUNT(*) AS rows_cnt,
       CAST(100.0 * COUNT(*) / NULLIF(SUM(COUNT(*)) OVER(), 0) AS DECIMAL(5,2)) AS pct
FROM vietnam_ecommerce.shopee_orders
GROUP BY order_status
ORDER BY rows_cnt DESC;

SELECT COUNT(*) AS rows_cnt, COUNT(DISTINCT shop_name) AS shops_cnt,
       MIN(created_time) AS min_dt, MAX(created_time) AS max_dt,
       DATEDIFF(DAY, MIN(created_time), MAX(created_time)) + 1 AS days_span
FROM vietnam_ecommerce.tiktok_orders;

SELECT order_status, COUNT(*) AS rows_cnt,
       CAST(100.0 * COUNT(*) / NULLIF(SUM(COUNT(*)) OVER(), 0) AS DECIMAL(5,2)) AS pct
FROM vietnam_ecommerce.tiktok_orders
GROUP BY order_status
ORDER BY rows_cnt DESC;

-- 2. Shopee: phân rã COMPLETED (thường vs trả hàng vs escrow <= 0) và TO_RETURN
SELECT
  CASE
    WHEN ISNULL(returned_quantity, 0) > 0 OR ISNULL(return_requested_qty, 0) > 0 THEN 'RETURNED_IN_COMPLETED'
    WHEN escrow_amount <= 0 THEN 'NON_RETURN_NEG_ZERO_ESCROW'
    ELSE 'NORMAL_COMPLETED'
  END AS grp,
  COUNT(*) AS rows_cnt,
  CAST(100.0 * COUNT(*) / SUM(COUNT(*)) OVER() AS DECIMAL(5,2)) AS pct,
  SUM(ISNULL(buyer_total_amount, 0)) AS sum_buyer_amt,
  SUM(ISNULL(escrow_amount, 0)) AS sum_escrow,
  SUM(ISNULL(return_shipping_fee, 0)) AS sum_ret_ship
FROM vietnam_ecommerce.shopee_orders
WHERE order_status = 'COMPLETED'
GROUP BY CASE
    WHEN ISNULL(returned_quantity, 0) > 0 OR ISNULL(return_requested_qty, 0) > 0 THEN 'RETURNED_IN_COMPLETED'
    WHEN escrow_amount <= 0 THEN 'NON_RETURN_NEG_ZERO_ESCROW'
    ELSE 'NORMAL_COMPLETED'
  END;

SELECT COUNT(*) AS neg_escrow_returned_rows,
       SUM(escrow_amount) AS sum_neg_escrow,
       SUM(return_shipping_fee) AS sum_ret_ship,
       SUM(buyer_total_amount) AS sum_buyer_amt
FROM vietnam_ecommerce.shopee_orders
WHERE order_status = 'COMPLETED' AND ISNULL(returned_quantity, 0) > 0 AND escrow_amount < 0;

-- 3. TikTok Shop: trả hàng sau giao (COMPLETED / DELIVERED có item_cancel_reason)
SELECT item_cancel_reason, COUNT(*) AS rows_cnt,
       CAST(100.0 * COUNT(*) / SUM(COUNT(*)) OVER() AS DECIMAL(5,2)) AS pct,
       SUM(ISNULL(item_sale_price, 0) * ISNULL(quantity, 1)) AS sale_gmv
FROM vietnam_ecommerce.tiktok_orders
WHERE order_status IN ('COMPLETED', 'DELIVERED')
  AND item_cancel_reason IS NOT NULL AND LTRIM(RTRIM(item_cancel_reason)) <> ''
GROUP BY item_cancel_reason
ORDER BY rows_cnt DESC;

-- 4. Hiệu ứng ngành thời trang theo gian hàng & nhóm hoàn lặp lại (Serial Returners)
SELECT TOP 10 shop_name, COUNT(*) AS total_rows,
       SUM(CASE WHEN order_status IN ('COMPLETED','DELIVERED') AND item_cancel_reason IS NOT NULL AND LTRIM(RTRIM(item_cancel_reason)) <> '' THEN 1 ELSE 0 END) AS post_ret,
       CAST(100.0 * SUM(CASE WHEN order_status IN ('COMPLETED','DELIVERED') AND item_cancel_reason IS NOT NULL AND LTRIM(RTRIM(item_cancel_reason)) <> '' THEN 1 ELSE 0 END)
            / NULLIF(SUM(CASE WHEN order_status IN ('COMPLETED','DELIVERED') THEN 1 ELSE 0 END), 0) AS DECIMAL(5,2)) AS post_ret_pct
FROM vietnam_ecommerce.tiktok_orders
GROUP BY shop_name
ORDER BY total_rows DESC;

SELECT shop_name, COUNT(*) AS total_rows,
       SUM(CASE WHEN ISNULL(returned_quantity, 0) > 0 OR order_status = 'TO_RETURN' THEN 1 ELSE 0 END) AS returned,
       CAST(100.0 * SUM(CASE WHEN ISNULL(returned_quantity, 0) > 0 OR order_status = 'TO_RETURN' THEN 1 ELSE 0 END)
            / NULLIF(SUM(CASE WHEN order_status IN ('COMPLETED','TO_RETURN') THEN 1 ELSE 0 END), 0) AS DECIMAL(5,2)) AS ret_pct,
       SUM(ISNULL(return_shipping_fee, 0)) AS ret_ship_fee
FROM vietnam_ecommerce.shopee_orders
GROUP BY shop_name
ORDER BY total_rows DESC;

WITH b AS (
  SELECT buyer_user_id,
         SUM(CASE WHEN ISNULL(returned_quantity, 0) > 0 THEN 1 ELSE 0 END) AS ret_rows,
         SUM(CASE WHEN order_status = 'CANCELLED' THEN 1 ELSE 0 END) AS cancel_rows
  FROM vietnam_ecommerce.shopee_orders
  GROUP BY buyer_user_id
)
SELECT COUNT(*) AS total_distinct_buyers,
       SUM(CASE WHEN ret_rows >= 1 THEN 1 ELSE 0 END) AS buyers_1plus_ret,
       SUM(CASE WHEN ret_rows >= 2 THEN 1 ELSE 0 END) AS buyers_2plus_ret,
       SUM(CASE WHEN ret_rows >= 3 THEN 1 ELSE 0 END) AS buyers_3plus_ret,
       SUM(CASE WHEN ret_rows >= 2 THEN ret_rows ELSE 0 END) AS ret_rows_from_repeat,
       SUM(ret_rows) AS total_ret_rows,
       MAX(ret_rows) AS max_ret_single_buyer
FROM b;

-- 5. AOV đơn thường vs đơn hoàn & Kiểm chứng các hướng bị loại (SLA, lệch ship, huỷ đơn)
SELECT 'Shopee_Normal' AS grp, COUNT(*) AS n, AVG(buyer_total_amount) AS avg_amt FROM vietnam_ecommerce.shopee_orders WHERE order_status='COMPLETED' AND ISNULL(returned_quantity,0)=0 AND buyer_total_amount>0
UNION ALL
SELECT 'Shopee_Returned', COUNT(*), AVG(buyer_total_amount) FROM vietnam_ecommerce.shopee_orders WHERE order_status='COMPLETED' AND ISNULL(returned_quantity,0)>0 AND buyer_total_amount>0
UNION ALL
SELECT 'TikTok_Normal', COUNT(*), AVG(item_sale_price*quantity) FROM vietnam_ecommerce.tiktok_orders WHERE order_status IN ('COMPLETED','DELIVERED') AND (item_cancel_reason IS NULL OR LTRIM(RTRIM(item_cancel_reason))='')
UNION ALL
SELECT 'TikTok_PostReturn', COUNT(*), AVG(item_sale_price*quantity) FROM vietnam_ecommerce.tiktok_orders WHERE order_status IN ('COMPLETED','DELIVERED') AND item_cancel_reason IS NOT NULL AND LTRIM(RTRIM(item_cancel_reason))<>'';

SELECT COUNT(*) AS ship_overcharge_rows
FROM vietnam_ecommerce.shopee_orders
WHERE actual_shipping_fee > estimated_shipping_fee;

SELECT COUNT(*) AS has_rts_sla,
       SUM(CASE WHEN rts_time > rts_sla_time THEN 1 ELSE 0 END) AS late_rts
FROM vietnam_ecommerce.tiktok_orders
WHERE rts_sla_time IS NOT NULL AND rts_time IS NOT NULL;
