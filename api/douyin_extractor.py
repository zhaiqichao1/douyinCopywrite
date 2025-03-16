#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import os
import time
from pathlib import Path
from typing import List, Dict, Optional, Union

import requests
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.text import Text

logger = logging.getLogger("douyin_extractor")
console = Console()

class DouyinExtractor:
    """抖音文案提取器，使用API方式获取抖音视频文案"""
    
    def __init__(self, retry_times=3, timeout=30):
        self.retry_times = retry_times
        self.timeout = timeout
        self.console = Console()
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            transient=True
        )
        
        # API相关请求头
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/109.0.0.0 Safari/537.36",
            "Referer": "https://www.douyin.com/",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Accept": "application/json, text/plain, */*"
        }
    
    def extract_aweme_info(self, aweme_id: str) -> Optional[Dict]:
        """
        通过API提取单个抖音作品的信息
        :param aweme_id: 抖音作品ID
        :return: 作品信息字典或None
        """
        api_url = f"https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id={aweme_id}"
        
        for attempt in range(self.retry_times):
            try:
                response = requests.get(api_url, headers=self.headers, timeout=self.timeout)
                
                if response.status_code != 200:
                    logger.warning(f"请求失败，状态码: {response.status_code}，重试中... ({attempt+1}/{self.retry_times})")
                    continue
                
                data = response.json()
                
                # 检查API返回是否成功
                if data.get("status_code") == 0 and "aweme_detail" in data:
                    logger.info(f"成功获取抖音作品信息: {aweme_id}")
                    return data["aweme_detail"]
                else:
                    logger.warning(f"API返回错误: {data.get('status_msg', '未知错误')}")
                    
            except Exception as e:
                logger.error(f"提取作品信息出错: {str(e)}")
                
            # 重试前延迟
            time.sleep(1.5)
                
        logger.error(f"提取作品信息失败，已达到最大重试次数: {aweme_id}")
        return None
    
    def extract_aweme_caption(self, aweme_detail: Dict) -> str:
        """
        从作品详情中提取文案
        :param aweme_detail: 作品详情
        :return: 文案文本
        """
        # 提取文案 (desc字段)
        caption = aweme_detail.get("desc", "")
        
        # 提取额外文本内容 (如长文本)
        if "long_video" in aweme_detail and aweme_detail["long_video"].get("long_text"):
            caption += "\n\n" + aweme_detail["long_video"]["long_text"]
            
        return caption
    
    def extract_by_urls(self, urls: List[str], save_path: Union[str, Path]) -> None:
        """
        批量提取多个抖音链接的文案
        :param urls: 抖音链接列表
        :param save_path: 保存路径
        """
        save_path = Path(save_path)
        save_path.mkdir(parents=True, exist_ok=True)
        
        start_time = time.time()
        total_count = len(urls)
        success_count = 0
        
        # 显示提取信息面板
        self.console.print(Panel(
            Text.assemble(
                ("文案提取配置\n", "bold cyan"),
                (f"总数: {total_count} 个作品\n", "cyan"),
                (f"保存路径: {save_path}\n", "cyan"),
            ),
            title="抖音文案提取器",
            border_style="cyan"
        ))
        
        # 合并的文案文件
        combined_file = save_path / "所有文案.txt"
        with open(combined_file, "w", encoding="utf-8") as combined:
            combined.write(f"=== 抖音文案合集 (共{total_count}个) ===\n\n")
        
        with self.progress:
            task = self.progress.add_task("[cyan]📝 提取文案进度", total=total_count)
            
            for i, url in enumerate(urls):
                try:
                    # 提取作品ID
                    aweme_id = self._extract_aweme_id_from_url(url)
                    if not aweme_id:
                        self.console.print(f"[yellow]⚠️  无法从URL提取作品ID: {url}[/]")
                        continue
                    
                    # 获取作品详情
                    aweme_detail = self.extract_aweme_info(aweme_id)
                    if not aweme_detail:
                        self.console.print(f"[yellow]⚠️  无法获取作品详情: {url}[/]")
                        continue
                    
                    # 提取文案
                    caption = self.extract_aweme_caption(aweme_detail)
                    
                    # 保存单独文件
                    file_name = f"{i+1:03d}_{aweme_id}_文案.txt"
                    self._save_caption(save_path / file_name, caption)
                    
                    # 追加到合并文件
                    with open(combined_file, "a", encoding="utf-8") as combined:
                        combined.write(f"------- 文案 {i+1:03d} -------\n")
                        combined.write(f"作品ID: {aweme_id}\n")
                        combined.write(f"链接: {url}\n\n")
                        combined.write(f"{caption}\n\n\n")
                    
                    # 同时保存JSON数据
                    self._save_json(save_path / f"{i+1:03d}_{aweme_id}_数据.json", aweme_detail)
                    
                    success_count += 1
                    self.progress.update(task, advance=1)
                    
                except Exception as e:
                    self.console.print(f"[red]❌ 提取失败: {str(e)}[/]")
                    self.progress.update(task, advance=1)
        
        # 显示完成统计
        end_time = time.time()
        duration = end_time - start_time
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        
        self.console.print(Panel(
            Text.assemble(
                ("文案提取完成\n", "bold green"),
                (f"成功: {success_count}/{total_count}\n", "green"),
                (f"用时: {minutes}分{seconds}秒\n", "green"),
                (f"保存位置: {save_path}\n", "green"),
                (f"合并文件: {combined_file.name}\n", "green"),
            ),
            title="提取统计",
            border_style="green"
        ))
    
    def _extract_aweme_id_from_url(self, url: str) -> Optional[str]:
        """
        从URL中提取抖音作品ID
        :param url: 抖音链接
        :return: 作品ID或None
        """
        try:
            # 处理分享短链接 - 需要先解析重定向
            if "v.douyin.com" in url:
                response = requests.head(url, headers=self.headers, allow_redirects=True)
                url = response.url
            
            # 从标准URL中提取
            if "/video/" in url:
                aweme_id = url.split("/video/")[1].split("/")[0].split("?")[0]
                return aweme_id
            
            # 直接从参数中提取
            elif "aweme_id=" in url:
                import re
                match = re.search(r"aweme_id=(\d+)", url)
                if match:
                    return match.group(1)
            
            return None
        except Exception as e:
            logger.error(f"提取作品ID出错: {str(e)}")
            return None
    
    def _save_caption(self, filepath: Path, caption: str) -> None:
        """保存文案到文本文件"""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(caption)
        except Exception as e:
            logger.error(f"保存文案失败: {filepath}, 错误: {str(e)}")
    
    def _save_json(self, filepath: Path, data: dict) -> None:
        """保存JSON数据"""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, ensure_ascii=False, indent=2, fp=f)
        except Exception as e:
            logger.error(f"保存JSON失败: {filepath}, 错误: {str(e)}") 