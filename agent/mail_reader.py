#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
极简版Outlook邮件扫描器
只做一件事：扫描邮件 → 匹配标题 → 上报内容
"""

import os
import json
import time
import datetime
import requests
import win32com.client

# 配置
CONFIG = {
    'api_base': 'http://localhost:8000',
    'mail_folder': '收件箱',
    'scan_interval': 300,  # 扫描间隔，秒
    'subject_keywords': ['转测', '版本发布', '提测'],
    'processed_file': 'processed_mails.json',
}


def load_processed_ids():
    """加载已处理的邮件ID"""
    if os.path.exists(CONFIG['processed_file']):
        with open(CONFIG['processed_file'], 'r', encoding='utf-8') as f:
            return set(json.load(f).get('ids', []))
    return set()


def save_processed_id(mail_id):
    """保存已处理的邮件ID"""
    processed_ids = load_processed_ids()
    processed_ids.add(str(mail_id))
    with open(CONFIG['processed_file'], 'w', encoding='utf-8') as f:
        json.dump({'ids': list(processed_ids)}, f)


def is_match(subject):
    """标题是否包含关键词"""
    return any(k in subject for k in CONFIG['subject_keywords'])


def send_to_factory(mail_info):
    """上报到待执行队列"""
    try:
        data = {
            'branchName': '默认分支',
            'version': '',
            'modelsStr': '自动识别',
            'status': 'pending',
            'reason': '邮件自动识别',
            'mailSubject': mail_info['subject'],
            'mailSender': mail_info['sender'],
            'mailBody': mail_info['body'][:3000],
            'receivedAt': mail_info['time'],
        }
        response = requests.post(f"{CONFIG['api_base']}/api/v1/version-queue/", json=data, timeout=10)
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"上报失败: {e}")
        return False


def scan_mails():
    """执行一次扫描"""
    processed_ids = load_processed_ids()
    count = 0

    try:
        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
        folder = outlook.GetDefaultFolder(6)  # 收件箱
        cutoff = datetime.datetime.now() - datetime.timedelta(hours=1)

        mails = folder.Items
        mails.Sort("[ReceivedTime]", True)

        for mail in mails:
            try:
                if mail.ReceivedTime.timestamp() < cutoff.timestamp():
                    break

                mail_id = str(mail.EntryID)
                subject = mail.Subject

                if mail_id in processed_ids or not is_match(subject):
                    continue

                mail_info = {
                    'subject': subject,
                    'sender': mail.SenderEmailAddress,
                    'body': mail.Body,
                    'time': mail.ReceivedTime.strftime('%Y-%m-%d %H:%M:%S'),
                }

                print(f"\n📧 {subject}")
                print(f"   发件人: {mail.SenderName}")

                if send_to_factory(mail_info):
                    save_processed_id(mail_id)
                    count += 1
                    print(f"   ✅ 已上报")
                else:
                    print(f"   ❌ 上报失败")

            except Exception:
                continue

    except Exception as e:
        print(f"扫描异常: {e}")

    if count > 0:
        print(f"\n📊 本次处理了 {count} 封邮件")
    return count


def main():
    print("=" * 50)
    print("  自动化工厂 - 极简邮件扫描器")
    print(f"  扫描间隔: {CONFIG['scan_interval']} 秒")
    print(f"  匹配关键词: {CONFIG['subject_keywords']}")
    print("=" * 50)

    while True:
        print(f"\n🕐 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 开始扫描...")
        scan_mails()
        time.sleep(CONFIG['scan_interval'])


if __name__ == '__main__':
    main()
